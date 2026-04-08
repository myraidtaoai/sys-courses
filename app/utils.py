"""
Shared utilities for the Affective Computing Streamlit app.

Data loading, embedding extraction, and split logic — mirrors the
classification_extra_data.ipynb notebook exactly.
"""

import os
import re
import json
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
import joblib

import streamlit as st

# ── Paths (relative to repo root) ────────────────────────────────────────────
REPO_ROOT     = Path(__file__).parent.parent
DATA_ROOT     = REPO_ROOT / "data"
FER_ROOT      = DATA_ROOT / "FER-2013"
TRAINING_SET  = DATA_ROOT / "training_set"
ANN_PATH      = TRAINING_SET / "annotations.csv"
CACHE_DIR     = REPO_ROOT / "app" / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR = REPO_ROOT / "embeddings"
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_STORE_DIR = REPO_ROOT / "models" / "saved_classifiers"
MODEL_STORE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_MANIFEST = MODEL_STORE_DIR / "manifest.json"

CLIP_CACHE    = EMBEDDINGS_DIR / "clip_embeddings.npz"
SIG_CACHE     = EMBEDDINGS_DIR / "siglip2_embeddings.npz"
LEGACY_CLIP_CACHE = CACHE_DIR / "clip_embeddings.npz"
LEGACY_SIG_CACHE  = CACHE_DIR / "siglip2_embeddings.npz"

SEED = 42
LABEL_MAP = {"neutral": 0, "happy": 1}
IDX_TO_LABEL = {0: "neutral", 1: "happy"}


def get_torch_device():
    """Return a stable torch device for this app.

    The default is CPU for stability on macOS Streamlit sessions.
    Set AFFE_COMPUTING_DEVICE=auto|cuda|mps|cpu to override.
    """
    import torch

    choice = os.getenv("AFFE_COMPUTING_DEVICE", "cpu").strip().lower()
    if choice == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if choice == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    if choice == "auto":
        if torch.backends.mps.is_available():
            return torch.device("mps")
        if torch.cuda.is_available():
            return torch.device("cuda")
    return torch.device("cpu")


def get_mlflow_tracking_uri():
    """Return a unified MLflow tracking URI for Streamlit pages and MLflow UI."""
    env_uri = os.getenv("MLFLOW_TRACKING_URI", "").strip()
    if env_uri:
        return env_uri
    return str(REPO_ROOT / "mlruns")


def get_mlflow_ui_command():
    """Return the recommended CLI command to launch MLflow UI for the active URI."""
    uri = get_mlflow_tracking_uri()

    # For local file stores, point MLflow UI to the same directory used by Streamlit logging.
    if uri.startswith("file://"):
        return f'mlflow ui --backend-store-uri "{uri[7:]}" --port 5000'
    if "://" not in uri:
        return f'mlflow ui --backend-store-uri "{uri}" --port 5000'

    # For remote tracking servers, MLflow UI should connect to that URI directly.
    return f'MLFLOW_TRACKING_URI="{uri}" mlflow ui --port 5000'


def _slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(text)).strip("_").lower()


def _read_model_manifest():
    if MODEL_MANIFEST.exists():
        try:
            with open(MODEL_MANIFEST, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def _write_model_manifest(manifest):
    with open(MODEL_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def save_trained_classifier(combo_key, clf):
    """Persist a fitted classifier and register it in the manifest."""
    filename = f"{_slugify(combo_key)}.joblib"
    model_path = MODEL_STORE_DIR / filename
    joblib.dump(clf, model_path)

    manifest = _read_model_manifest()
    manifest[combo_key] = str(model_path)
    _write_model_manifest(manifest)
    return model_path


def load_saved_classifiers():
    """Load all saved classifiers from manifest (combo_key -> estimator)."""
    loaded = {}
    manifest = _read_model_manifest()

    for combo_key, model_path in manifest.items():
        p = Path(model_path)
        if not p.exists():
            continue
        try:
            loaded[combo_key] = joblib.load(p)
        except Exception:
            continue

    return loaded


# ── Data loading ─────────────────────────────────────────────────────────────

def normalize_label(raw):
    raw = str(raw).strip().lower()
    if raw in ("happy", "happiness", "1"):
        return "happy"
    if raw in ("neutral", "0"):
        return "neutral"
    return None


def collect_fer2013_df():
    """Collect all FER-2013 image paths with labels (neutral + happy only)."""
    rows = []
    for split in ("train", "test"):
        for label_dir in (FER_ROOT / split).iterdir():
            norm = normalize_label(label_dir.name)
            if norm is None:
                continue
            for img_path in label_dir.glob("*.jpg"):
                rows.append({"filepath": str(img_path), "label": norm, "source": "FER-2013"})
            for img_path in label_dir.glob("*.png"):
                rows.append({"filepath": str(img_path), "label": norm, "source": "FER-2013"})
    return pd.DataFrame(rows)


def collect_training_set_df():
    """Collect training_set images via annotations.csv."""
    df = pd.read_csv(ANN_PATH, header=None, names=["filename", "label"])
    actual = {f.lower(): f for f in os.listdir(TRAINING_SET) if f.lower().endswith(".jpg")}
    df["resolved"] = df["filename"].apply(lambda x: actual.get(x.lower()))
    df = df[df["resolved"].notna()].copy()
    df["filepath"] = df["resolved"].apply(lambda f: str(TRAINING_SET / f))
    df["source"] = "training_set"
    return df[["filepath", "label", "source"]]


@st.cache_data(show_spinner="Loading datasets…")
def load_combined_df(fer_sample_frac=0.20):
    """Combine FER-2013 (downsampled) + training_set, return combined + splits."""
    from sklearn.model_selection import train_test_split

    fer_df = collect_fer2013_df()
    fer_small = fer_df.groupby("label", group_keys=False).apply(
        lambda g: g.sample(frac=fer_sample_frac, random_state=SEED)
    ).reset_index(drop=True)

    ts_df = collect_training_set_df()
    combined = pd.concat([fer_small, ts_df], ignore_index=True)
    combined["label_idx"] = combined["label"].map(LABEL_MAP)

    train_df, temp_df = train_test_split(combined, test_size=0.30, stratify=combined["label_idx"], random_state=SEED)
    val_df,  test_df  = train_test_split(temp_df,  test_size=0.50, stratify=temp_df["label_idx"],  random_state=SEED)

    return (
        combined.reset_index(drop=True),
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


# ── Embedding models ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading CLIP model…")
def load_clip():
    from transformers import CLIPModel, CLIPProcessor
    proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()
    return proc, model


@st.cache_resource(show_spinner="Loading SigLIP2 model…")
def load_siglip():
    from transformers import AutoModel, AutoProcessor
    proc  = AutoProcessor.from_pretrained("google/siglip2-base-patch16-224")
    model = AutoModel.from_pretrained("google/siglip2-base-patch16-224")
    model.eval()
    return proc, model


def _to_embedding_tensor(raw_out):
    """Convert model outputs from different HF APIs into a single embedding tensor."""
    import torch
    if torch.is_tensor(raw_out):
        return raw_out

    if hasattr(raw_out, "pooler_output") and raw_out.pooler_output is not None:
        return raw_out.pooler_output

    if hasattr(raw_out, "image_embeds") and raw_out.image_embeds is not None:
        return raw_out.image_embeds

    if hasattr(raw_out, "last_hidden_state") and raw_out.last_hidden_state is not None:
        return raw_out.last_hidden_state[:, 0, :]

    if isinstance(raw_out, (tuple, list)):
        for item in raw_out:
            if torch.is_tensor(item):
                return item

    raise TypeError(f"Unsupported embedding output type: {type(raw_out).__name__}")


def extract_embeddings(df, processor, model, model_type, device=None, batch_size=32):
    """
    Extract L2-normalized embeddings for all images in *df*.

    Parameters
    ----------
    model_type : "clip" | "siglip"

    Returns
    -------
    embs   : np.ndarray (n, dim)
    labels : np.ndarray (n,)
    """
    import torch
    import torch.nn.functional as F
    if device is None:
        device = get_torch_device()
    model = model.to(device)
    all_embs, all_labels = [], []

    with torch.no_grad():
        for start in range(0, len(df), batch_size):
            batch = df.iloc[start : start + batch_size]
            images = []
            for _, row in batch.iterrows():
                try:
                    img = Image.open(row["filepath"]).convert("RGB")
                except Exception:
                    img = Image.new("RGB", (224, 224))
                images.append(img)

            inputs = processor(images=images, return_tensors="pt").to(device)
            if model_type == "clip":
                raw_out = model.get_image_features(**inputs)
            else:
                if hasattr(model, "get_image_features"):
                    raw_out = model.get_image_features(**inputs)
                else:
                    raw_out = model.vision_model(**inputs)

            embs = _to_embedding_tensor(raw_out)
            embs = F.normalize(embs, p=2, dim=-1)
            all_embs.append(embs.cpu().float().numpy())
            all_labels.extend(batch["label_idx"].tolist())

    return np.vstack(all_embs), np.array(all_labels)


def get_or_compute_embeddings(train_df, val_df, test_df):
    """
    Load embeddings from .npz cache files, or compute and save them.
    Returns dict with keys clip/siglip2, each containing X_train/val/test + y_train/y_test.
    """
    result = {}

    for name, primary_path, legacy_path, model_type, loader_fn in [
        ("clip",    CLIP_CACHE, LEGACY_CLIP_CACHE, "clip",   load_clip),
        ("siglip2", SIG_CACHE,  LEGACY_SIG_CACHE,  "siglip", load_siglip),
    ]:
        if primary_path.exists():
            data = np.load(primary_path)
            result[name] = {
                "X_train": data["X_train"],
                "X_val":   data["X_val"],
                "X_test":  data["X_test"],
                "y_train": data["y_train"],
                "y_test":  data["y_test"],
            }
        elif legacy_path.exists():
            data = np.load(legacy_path)
            result[name] = {
                "X_train": data["X_train"],
                "X_val":   data["X_val"],
                "X_test":  data["X_test"],
                "y_train": data["y_train"],
                "y_test":  data["y_test"],
            }
        else:
            import torch
            proc, model = loader_fn()
            device = get_torch_device()
            X_train, y_train = extract_embeddings(train_df, proc, model, model_type, device)
            X_val,   _       = extract_embeddings(val_df,   proc, model, model_type, device)
            X_test,  y_test  = extract_embeddings(test_df,  proc, model, model_type, device)
            np.savez_compressed(
                primary_path,
                X_train=X_train, X_val=X_val, X_test=X_test,
                y_train=y_train, y_test=y_test,
            )
            result[name] = {
                "X_train": X_train, "X_val": X_val, "X_test": X_test,
                "y_train": y_train, "y_test": y_test,
            }

    return result


# ── Classifiers definition ────────────────────────────────────────────────────

def get_classifiers():
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
    from xgboost import XGBClassifier

    return {
        "LogReg (linear probe)": LogisticRegression(C=0.1, max_iter=1000, random_state=SEED),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            eval_metric="logloss", random_state=SEED, verbosity=0,
        ),
        "Deep Probe (MLP)": MLPClassifier(
            hidden_layer_sizes=(512, 256, 128), activation="relu",
            solver="adam", batch_size=32, max_iter=300,
            early_stopping=True, validation_fraction=0.1,
            random_state=SEED,
        ),
    }


EMBEDDING_NAMES  = ["CLIP", "SigLIP2"]
CLASSIFIER_NAMES = ["LogReg (linear probe)", "XGBoost", "Deep Probe (MLP)"]
COMBO_KEYS       = [f"{e} + {c}" for e in EMBEDDING_NAMES for c in CLASSIFIER_NAMES]

EMB_KEY_MAP = {"CLIP": "clip", "SigLIP2": "siglip2"}  # display → cache key
