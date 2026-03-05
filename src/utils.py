"""
Shared utilities: config loading, global seed, and file hashing.
Ensures deterministic behaviour across pipeline stages.
"""
from pathlib import Path
import hashlib
import yaml


def load_params(params_path: str = "params.yaml") -> dict:
    """Load YAML config from repo root (run from project root)."""
    path = Path(params_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {params_path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def set_global_seed(seed: int) -> None:
    """Set global random seed for numpy and sklearn reproducibility."""
    import numpy as np
    np.random.seed(seed)
    # sklearn uses numpy's global RNG when random_state is None in many APIs
    # We pass seed explicitly where needed; this backs up global state.


def get_file_hash(filepath: str | Path, algorithm: str = "sha256") -> str:
    """Return hex digest of file contents for reproducibility checks."""
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Not a file: {filepath}")
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
