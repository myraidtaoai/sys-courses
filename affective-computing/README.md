# Affective Computing — Facial Emotion Recognition

An interactive emotion recognition system that classifies facial expressions (**neutral** vs **happy**) using frozen vision-language embeddings (CLIP and SigLIP2) with lightweight trainable classifiers. Includes a full Streamlit dashboard for data exploration, model training, evaluation, and real-time inference.

## Overview

Rather than fine-tuning large vision models end-to-end, this project extracts frozen embeddings from two foundation models and trains lightweight classifiers on top. This makes the pipeline fast, reproducible, and hardware-friendly.

**Embedding models:**
- **CLIP ViT-B/32** (`openai/clip-vit-base-patch32`) — 512-dim embeddings
- **SigLIP2 ViT-B/16** (`google/siglip2-base-patch16-224`) — 768-dim embeddings

**Classifiers trained on embeddings:**
- Logistic Regression (linear probe baseline)
- XGBoost
- Deep Probe (3-layer MLP)

## Results

| Embedding + Classifier | Accuracy | F1 | Precision | Recall |
|---|---|---|---|---|
| SigLIP2 + Deep Probe | **0.942** | **0.949** | 0.954 | 0.944 |
| SigLIP2 + XGBoost | 0.930 | 0.939 | 0.941 | 0.938 |
| CLIP + Deep Probe | 0.932 | 0.941 | 0.947 | 0.934 |
| CLIP + XGBoost | 0.923 | 0.934 | 0.923 | 0.944 |
| SigLIP2 + LogReg | 0.883 | 0.905 | 0.848 | 0.970 |
| CLIP + LogReg | 0.870 | 0.897 | 0.826 | 0.980 |

All models evaluated with 5-fold cross-validation and held-out test set.

## Dataset

- **FER-2013** — Public facial expression dataset filtered to neutral/happy classes (20% sample used)
- **Custom training set** — 500 hand-curated face images with labels in `data/training_set/annotations.csv`
- Combined and split 70% / 15% / 15% (train / val / test) with stratification

## Project Structure

```
affective-computing/
├── app/
│   ├── streamlit_app.py          # Dashboard entry point
│   ├── utils.py                  # Shared utilities (embeddings, classifiers, data loading)
│   └── pages/
│       ├── 1_Data_Exploration.py # Dataset overview, t-SNE/UMAP visualizations
│       ├── 2_Model_Training.py   # Training with cross-validation and MLflow logging
│       ├── 3_Model_Evaluation.py # Metrics, confusion matrices, ROC curves
│       └── 4_Model_Inference.py  # Upload an image for live prediction
├── data/
│   ├── FER-2013/                 # train/ and test/ splits with neutral/ and happy/ subdirs
│   └── training_set/             # Custom images + annotations.csv
├── embeddings/                   # Pre-computed .npz embedding caches
├── models/saved_classifiers/     # Trained .joblib models and results cache
├── notebooks/                    # Exploratory Jupyter notebooks
├── mlruns/                       # MLflow experiment tracking
└── requirements.txt
```

## Setup

**Requirements:** Python 3.8+

```bash
# Clone the repo
git clone https://github.com/myraidtaoai/affective-computing.git
cd affective-computing

# Create and activate a virtual environment
python -m venv .affecomp
source .affecomp/bin/activate  # Windows: .affecomp\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Dashboard

```bash
streamlit run app/streamlit_app.py
```

Opens at `http://localhost:8501`. The four pages cover the full ML workflow:

| Page | What it does |
|---|---|
| Data Exploration | Sample images, class distribution, embedding projections (t-SNE / UMAP) |
| Model Training | Train all 6 embedding+classifier combos, 5-fold CV, logs to MLflow |
| Model Evaluation | Per-model metrics, confusion matrices, ROC curves, comparison table |
| Model Inference | Upload a face image and get a neutral/happy prediction |

**Optional: view MLflow experiment runs**

```bash
mlflow ui --backend-store-uri mlruns --port 5000
# Open http://127.0.0.1:5000
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `AFFE_COMPUTING_DEVICE` | `auto` | Device to use: `cpu`, `cuda`, `mps`, or `auto` |
| `MLFLOW_TRACKING_URI` | `mlruns` | MLflow backend storage path |

The project runs on CPU, NVIDIA CUDA, and Apple Silicon (MPS).

## Tech Stack

| Category | Libraries |
|---|---|
| Dashboard | Streamlit |
| Deep learning | PyTorch, TorchVision, Transformers, Accelerate |
| Classical ML | scikit-learn, XGBoost |
| Experiment tracking | MLflow |
| Visualization | Plotly, Matplotlib, Seaborn, UMAP |
| Data | Pandas, NumPy, Pillow |
