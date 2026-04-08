"""
Page 3 — Model Evaluation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, f1_score, precision_score, recall_score,
)

from app.utils import (
    load_combined_df, get_or_compute_embeddings, load_saved_classifiers,
    EMBEDDING_NAMES, CLASSIFIER_NAMES, EMB_KEY_MAP, SEED, MODEL_STORE_DIR,
)

EVAL_RESULTS_CACHE = MODEL_STORE_DIR / "eval_results_cache.json"

st.set_page_config(page_title="Model Evaluation", page_icon="📊", layout="wide")
st.title("📊 Model Evaluation")

# ── Load data ─────────────────────────────────────────────────────────────────
if "combined_df" not in st.session_state:
    combined_df, train_df, val_df, test_df = load_combined_df()
    st.session_state.update({
        "combined_df": combined_df,
        "train_df": train_df,
        "val_df":   val_df,
        "test_df":  test_df,
    })

train_df = st.session_state["train_df"]
val_df   = st.session_state["val_df"]
test_df  = st.session_state["test_df"]

# ── Ensure embeddings ─────────────────────────────────────────────────────────
if "emb_data" not in st.session_state:
    if st.button("Load / Compute Embeddings"):
        with st.spinner("Loading embeddings…"):
            emb_data = get_or_compute_embeddings(train_df, val_df, test_df)
            st.session_state["emb_data"] = emb_data
        st.success("Embeddings ready.")
    else:
        st.info("Embeddings must be loaded before evaluation.")
        st.stop()

emb_data = st.session_state["emb_data"]

# ── Load saved classifiers from disk ─────────────────────────────────────────
saved_clfs = load_saved_classifiers()
if not saved_clfs:
    st.warning(
        "No saved classifiers found on disk. "
        "Train models on the Model Training page first."
    )
    st.stop()

trained_clfs = {}
for key, clf in saved_clfs.items():
    if " + " not in key:
        continue
    emb_name = key.split(" + ")[0]
    emb_key = EMB_KEY_MAP.get(emb_name)
    if emb_key is None:
        continue

    X_te = emb_data[emb_key]["X_test"]
    y_te = emb_data[emb_key]["y_test"]
    trained_clfs[key] = (clf, X_te, y_te)

if not trained_clfs:
    st.warning("Saved classifiers were found, but none matched known embedding keys.")
    st.stop()

# ── Load or compute evaluation results ───────────────────────────────────────
_eval_cached = "eval_results" in st.session_state

if not _eval_cached and EVAL_RESULTS_CACHE.exists():
    with open(EVAL_RESULTS_CACHE) as _f:
        st.session_state["eval_results"] = json.load(_f)
    _eval_cached = True

_col_eval, _col_reeval = st.columns([3, 1])
_force_eval = _col_reeval.button("Refresh Results", disabled=not _eval_cached)

if _force_eval:
    EVAL_RESULTS_CACHE.unlink(missing_ok=True)
    st.session_state.pop("eval_results", None)
    _eval_cached = False

if not _eval_cached:
    results = {}
    for key, (clf, X_te, y_te) in trained_clfs.items():
        y_pred = clf.predict(X_te)
        results[key] = {
            "accuracy":  round(accuracy_score(y_te, y_pred), 3),
            "f1":        round(f1_score(y_te, y_pred), 3),
            "precision": round(precision_score(y_te, y_pred), 3),
            "recall":    round(recall_score(y_te, y_pred), 3),
        }
    st.session_state["eval_results"] = results
    with open(EVAL_RESULTS_CACHE, "w") as _f:
        json.dump(results, _f)
else:
    results = st.session_state["eval_results"]
    _col_eval.success("Cached evaluation results loaded.")

best_key = max(results, key=lambda k: results[k]["f1"])

# ── Section 1: Results table ──────────────────────────────────────────────────
st.header("1. Test-Set Results")

results_df = pd.DataFrame(results).T.reset_index().rename(columns={"index": "Combination"})
results_df = results_df.sort_values("f1", ascending=False).reset_index(drop=True)

def highlight_best(row):
    is_best = row["Combination"] == best_key
    return ["background-color: #c6efce" if is_best else "" for _ in row]

st.dataframe(
    results_df.style.apply(highlight_best, axis=1),
    width="content",
    hide_index=True,
)
st.success(f"Best combination: **{best_key}** — Test F1 = {results[best_key]['f1']:.3f}")

# ── Section 2: F1 heatmap ─────────────────────────────────────────────────────
st.header("2. F1 Score Heatmap")

f1_matrix = pd.DataFrame(
    index=CLASSIFIER_NAMES,
    columns=EMBEDDING_NAMES,
    dtype=float,
)
for emb_name in EMBEDDING_NAMES:
    for clf_name in CLASSIFIER_NAMES:
        key = f"{emb_name} + {clf_name}"
        if key in results:
            f1_matrix.loc[clf_name, emb_name] = results[key]["f1"]

fig_heat = px.imshow(
    f1_matrix.astype(float),
    text_auto=".3f",
    color_continuous_scale="YlGnBu",
    zmin=0.5, zmax=1.0,
    title="F1 Score — Classifier × Embedding Model",
    labels={"x": "Embedding", "y": "Classifier", "color": "F1"},
)
fig_heat.update_layout(height=320)
st.plotly_chart(fig_heat, width="content")

# ── Section 3: Multi-metric bar chart ────────────────────────────────────────
st.header("3. All Metrics Comparison")

metrics = ["accuracy", "f1", "precision", "recall"]
bar_df = results_df.melt(id_vars="Combination", value_vars=metrics,
                          var_name="Metric", value_name="Score")
fig_bar = px.bar(
    bar_df, x="Combination", y="Score", color="Metric",
    barmode="group", title="All Metrics — Test Set",
    range_y=[0.5, 1.0],
)
fig_bar.update_layout(height=400, xaxis_tickangle=-20)
st.plotly_chart(fig_bar, width="content")

# ── Section 4: Confusion matrix ───────────────────────────────────────────────
st.header("4. Confusion Matrix")

combo_choice = st.selectbox("Select combination", list(results.keys()),
                             index=list(results.keys()).index(best_key)
                             if best_key in results else 0)

clf_fit, X_te, y_te = trained_clfs[combo_choice]
y_pred = clf_fit.predict(X_te)
cm = confusion_matrix(y_te, y_pred)

fig_cm = ff.create_annotated_heatmap(
    cm,
    x=["Predicted neutral", "Predicted happy"],
    y=["True neutral",      "True happy"],
    colorscale="Blues",
    showscale=True,
)
fig_cm.update_layout(title=f"Confusion Matrix — {combo_choice}", height=350)
st.plotly_chart(fig_cm, width="content")

# ── Section 5: Classification report ─────────────────────────────────────────
st.header("5. Detailed Classification Report")

report_choice = st.selectbox(
    "Select combination for classification report",
    list(results.keys()),
    index=list(results.keys()).index(best_key) if best_key in results else 0,
    key="report_select",
)
clf_fit2, X_te2, y_te2 = trained_clfs[report_choice]
y_pred2 = clf_fit2.predict(X_te2)
report_dict = classification_report(y_te2, y_pred2,
                                     target_names=["neutral", "happy"],
                                     output_dict=True)
report_df = pd.DataFrame(report_dict).T.round(3)
st.dataframe(report_df, width="content")
