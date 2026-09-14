from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "raw"


def load_project_data() -> dict[str, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers_data.csv", parse_dates=["Join_Date"])
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    products = pd.read_csv(DATA_DIR / "products_data.csv")
    marketing = pd.read_csv(DATA_DIR / "marketing_data.csv", parse_dates=["Start_Date", "End_Date"])
    return {
        "customers": customers,
        "sales": sales,
        "products": products,
        "marketing": marketing,
    }


def build_feature_table(customers: pd.DataFrame, sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    sales_full = sales.merge(products, on="Product_ID", how="left")
    sales_full["Line_Amount"] = sales_full["Quantity"] * sales_full["Sale_Price"]
    reference_date = sales_full["Date"].max()

    agg = sales_full.groupby("Customer_ID").agg(
        Recency_Days=("Date", lambda x: (reference_date - x.max()).days),
        Frequency=("Sale_ID", "count"),
        Monetary=("Line_Amount", "sum"),
        Avg_Basket=("Line_Amount", "mean"),
        Nb_Categories=("Category", "nunique"),
        Last_Purchase_Date=("Date", "max"),
    ).reset_index()

    features = customers.merge(agg, on="Customer_ID", how="left")
    features["Recency_Days"] = features["Recency_Days"].fillna(9999)
    features["Frequency"] = features["Frequency"].fillna(0)
    features["Monetary"] = features["Monetary"].fillna(0)
    features["Avg_Basket"] = features["Avg_Basket"].fillna(0)
    features["Nb_Categories"] = features["Nb_Categories"].fillna(0)
    features["Tenure_Days"] = (reference_date - features["Join_Date"]).dt.days

    churn_threshold_days = 90
    features["Churn"] = (features["Recency_Days"] > churn_threshold_days).astype(int)
    features["CLV"] = features["Total_Spent"]
    return features


def prepare_model_matrix(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    feature_cols_num = [
        "Age",
        "Recency_Days",
        "Frequency",
        "Monetary",
        "Avg_Basket",
        "Nb_Categories",
        "Tenure_Days",
    ]
    feature_cols_cat = ["Gender", "Location"]

    df_model = features.copy()
    df_model = pd.get_dummies(df_model, columns=feature_cols_cat, drop_first=True)

    feature_cols = feature_cols_num + [
        c for c in df_model.columns if c.startswith(("Gender_", "Location_"))
    ]

    X = df_model[feature_cols]
    y = df_model["Churn"]
    return X, y, feature_cols


def train_churn_models(X: pd.DataFrame, y: pd.Series, threshold: float = 0.3) -> dict:
    result: dict = {"status": "trained", "models": {}, "report": {}}

    if y.nunique() < 2:
        result["status"] = "fallback"
        result["report"] = {
            "message": "Le jeu de données ne contient qu'une seule classe; l'entraînement supervisé est impossible."
        }
        return result

    if len(X) < 10:
        X_train, X_test = X.copy(), X.copy()
        y_train, y_test = y.copy(), y.copy()
        result["status"] = "fallback"
        result["report"] = {
            "message": "Le dataset est trop petit pour produire un split fiable; évaluation in-sample utilisée comme fallback."
        }
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=threshold,
            random_state=42,
            stratify=y,
        )

    if y_train.nunique() < 2 or y_test.nunique() < 2:
        X_train, X_test = X.copy(), X.copy()
        y_train, y_test = y.copy(), y.copy()
        result["status"] = "fallback"
        result["report"] = {
            "message": "Le split a supprimé une classe; la validation est relancée sur tout le dataset pour éviter un crash."
        }

    rf = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_proba_rf = rf.predict_proba(X_test)[:, 1]

    result["models"]["random_forest"] = {
        "accuracy": accuracy_score(y_test, y_pred_rf),
        "precision": precision_score(y_test, y_pred_rf, zero_division=0),
        "recall": recall_score(y_test, y_pred_rf, zero_division=0),
        "f1": f1_score(y_test, y_pred_rf, zero_division=0),
        "roc_auc": float(roc_auc_score(y_test, y_proba_rf)) if y_test.nunique() == 2 else None,
        "classification_report": classification_report(y_test, y_pred_rf, zero_division=0, output_dict=True),
    }

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    log_clf = LogisticRegression(max_iter=1000, random_state=42)
    try:
        log_clf.fit(X_train_scaled, y_train)
        y_pred_log = log_clf.predict(X_test_scaled)
        y_proba_log = log_clf.predict_proba(X_test_scaled)[:, 1]

        result["models"]["logistic_regression"] = {
            "accuracy": accuracy_score(y_test, y_pred_log),
            "precision": precision_score(y_test, y_pred_log, zero_division=0),
            "recall": recall_score(y_test, y_pred_log, zero_division=0),
            "f1": f1_score(y_test, y_pred_log, zero_division=0),
            "roc_auc": float(roc_auc_score(y_test, y_proba_log)) if y_test.nunique() == 2 else None,
            "classification_report": classification_report(y_test, y_pred_log, zero_division=0, output_dict=True),
        }
    except ValueError as exc:
        result["status"] = "fallback"
        result["report"]["logistic_regression"] = str(exc)
        result["models"]["logistic_regression"] = {"status": "skipped"}

    return result


def run_project_demo() -> dict:
    data = load_project_data()
    features = build_feature_table(data["customers"], data["sales"], data["products"])
    X, y, _ = prepare_model_matrix(features)
    result = train_churn_models(X, y)
    return {"features": features, "models": result}


if __name__ == "__main__":
    demo = run_project_demo()
    print("Dataset size:", demo["features"].shape)
    print("Churn distribution:", demo["features"]["Churn"].value_counts().to_dict())
    print("Status:", demo["models"]["status"])
    if demo["models"]["report"]:
        print("Report:", demo["models"]["report"])
    for model_name, payload in demo["models"]["models"].items():
        if isinstance(payload, dict) and "status" not in payload:
            print(f"{model_name}: accuracy={payload['accuracy']:.3f}, f1={payload['f1']:.3f}")
