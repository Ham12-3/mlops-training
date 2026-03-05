"""
Data stage: load a small public dataset (sklearn) and save to CSV.
Deterministic: sklearn datasets have fixed order.
"""
from pathlib import Path

import pandas as pd
from sklearn import datasets

from src.utils import load_params, set_global_seed


def main() -> None:
    params = load_params()
    set_global_seed(params["seed"])

    dataset_name = params["data"]["dataset"]
    raw_path = Path(params["data"]["raw_path"])

    if dataset_name == "breast_cancer":
        data = datasets.load_breast_cancer()
        X = data.data
        y = data.target
        columns = list(data.feature_names) + ["target"]
    elif dataset_name == "iris":
        data = datasets.load_iris()
        X = data.data
        y = data.target
        columns = list(data.feature_names) + ["target"]
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    df = pd.DataFrame(X, columns=data.feature_names)
    df["target"] = y

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_path, index=False)


if __name__ == "__main__":
    main()
