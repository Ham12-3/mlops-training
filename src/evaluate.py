"""
Evaluate stage: compute metrics and save predictions.
Writes metrics.json (DVC metrics) and artefacts/preds.csv.
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.utils import load_params


def main() -> None:
    params = load_params()

    model_path = Path(params["train"]["model_path"])
    test_path = Path(params["preprocess"]["output_test"])
    metrics_path = Path(params["evaluate"]["metrics_path"])
    preds_path = Path(params["evaluate"]["preds_path"])

    model = joblib.load(model_path)
    test_df = pd.read_csv(test_path)
    X_test = test_df.drop(columns=["target"])
    y_test = test_df["target"]

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
    }

    preds_path.parent.mkdir(parents=True, exist_ok=True)
    preds_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred})
    preds_df.to_csv(preds_path, index=False)

    with open(metrics_path, "w", encoding="utf-8") as f:
        import json
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
