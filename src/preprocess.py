"""
Preprocess stage: train/test split with fixed seed for reproducibility.
"""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils import load_params, set_global_seed


def main() -> None:
    params = load_params()
    set_global_seed(params["seed"])

    raw_path = Path(params["data"]["raw_path"])
    out_train = Path(params["preprocess"]["output_train"])
    out_test = Path(params["preprocess"]["output_test"])
    test_size = params["preprocess"]["test_size"]

    df = pd.read_csv(raw_path)
    if "target" not in df.columns:
        raise ValueError("Expected 'target' column in raw data")

    X = df.drop(columns=["target"])
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=params["seed"], stratify=y
    )

    out_train.parent.mkdir(parents=True, exist_ok=True)
    out_test.parent.mkdir(parents=True, exist_ok=True)

    train_df = X_train.copy()
    train_df["target"] = y_train
    test_df = X_test.copy()
    test_df["target"] = y_test

    train_df.to_csv(out_train, index=False)
    test_df.to_csv(out_test, index=False)


if __name__ == "__main__":
    main()
