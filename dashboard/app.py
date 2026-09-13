from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.project_pipeline import build_feature_table, load_project_data, prepare_model_matrix, train_churn_models


@st.cache_data
def load_dashboard_data():
    data = load_project_data()
    features = build_feature_table(data["customers"], data["sales"], data["products"])
    X, y, feature_cols = prepare_model_matrix(features)
    metrics = train_churn_models(X, y)
    return features, X, y, feature_cols, metrics


st.set_page_config(page_title="Segmentation client marketing", layout="wide")
st.title("Segmentation client & marketing IA")

features, X, y, feature_cols, metrics = load_dashboard_data()

st.subheader("Aperçu des clients")
st.dataframe(features[["Customer_ID", "Age", "Gender", "Location", "Recency_Days", "Frequency", "Monetary", "Churn", "CLV"]])

st.subheader("Résultat du modèle de churn")
st.write(metrics["status"])
if metrics.get("report"):
    st.info(metrics["report"])

for model_name, payload in metrics.get("models", {}).items():
    if isinstance(payload, dict) and "status" not in payload:
        st.markdown(f"### {model_name.replace('_', ' ').title()}")
        st.write({
            "accuracy": round(float(payload["accuracy"]), 3),
            "precision": round(float(payload["precision"]), 3),
            "recall": round(float(payload["recall"]), 3),
            "f1": round(float(payload["f1"]), 3),
            "roc_auc": round(float(payload["roc_auc"]), 3) if payload.get("roc_auc") is not None else None,
        })

st.subheader("Distribution du churn")
churn_counts = features["Churn"].value_counts().rename(index={0: "Non churn", 1: "Churn"})
st.bar_chart(churn_counts)
