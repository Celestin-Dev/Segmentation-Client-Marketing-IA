import pandas as pd

from src.project_pipeline import build_feature_table, train_churn_models


def test_build_feature_table_creates_churn_column():
    customers = pd.DataFrame(
        {
            "Customer_ID": [2001, 2002, 2003],
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [28, 35, 22],
            "Gender": ["Female", "Male", "Male"],
            "Location": ["New York", "Los Angeles", "Chicago"],
            "Join_Date": pd.to_datetime(["2022-05-10", "2022-06-15", "2022-07-20"]),
            "Total_Spent": [500.0, 750.0, 300.0],
        }
    )
    sales = pd.DataFrame(
        {
            "Sale_ID": [1, 2, 3],
            "Product_ID": [101, 102, 103],
            "Customer_ID": [2001, 2002, 2001],
            "Date": pd.to_datetime(["2023-01-15", "2023-01-16", "2023-01-17"]),
            "Quantity": [2, 1, 3],
            "Sale_Price": [50.0, 75.0, 30.0],
            "Channel": ["Online", "In-Store", "Online"],
        }
    )
    products = pd.DataFrame(
        {
            "Product_ID": [101, 102, 103],
            "Product_Name": ["T-shirt", "Jeans", "Sneakers"],
            "Category": ["Clothing", "Clothing", "Footwear"],
            "Price": [25.0, 75.0, 30.0],
            "Brand": ["Brand A", "Brand B", "Brand C"],
        }
    )

    features = build_feature_table(customers, sales, products)

    assert "Churn" in features.columns
    assert "Recency_Days" in features.columns
    assert "Tenure_Days" in features.columns
    assert set(features["Customer_ID"]) == {2001, 2002, 2003}


def test_train_churn_models_handles_small_dataset():
    X = pd.DataFrame({"Age": [20, 25, 30, 35, 40], "Recency_Days": [10, 15, 50, 100, 120]})
    y = pd.Series([0, 0, 0, 0, 1])

    result = train_churn_models(X, y, threshold=0.3)

    assert result["status"] in {"fallback", "trained"}
    assert "report" in result
