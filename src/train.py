"""
Train stage: fit a deterministic scikit-learn model and save as joblib.
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.utils import load_params, set_global_seed


def main() -> None:
    params = load_params()
    set_global_seed(params["seed"])

    train_path = Path(params["preprocess"]["output_train"])
    model_path = Path(params["train"]["model_path"])
    train_params = params["train"]

    df = pd.read_csv(train_path)
    X = df.drop(columns=["target"])
    y = df["target"]

    model = RandomForestClassifier(
        n_estimators=train_params["n_estimators"],
        max_depth=train_params["max_depth"],
        min_samples_split=train_params["min_samples_split"],
        min_samples_leaf=train_params["min_samples_leaf"],
        random_state=params["seed"],
    )
    model.fit(X, y)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


if __name__ == "__main__":
    main()
