#!/usr/bin/env python3
"""
Reproducibility check: run pipeline twice and assert metrics + model hash match.
Exits with code 0 on success, 1 on failure (with clear message).
"""
from pathlib import Path
import json
import subprocess
import sys

# Import after we know we're in repo root; params and utils live there
from src.utils import load_params, get_file_hash


def run_cmd(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run command; raise on non-zero exit."""
    result = subprocess.run(cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    return result


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    import os
    os.chdir(repo_root)
    params = load_params()
    metrics_path = Path(params["evaluate"]["metrics_path"])
    model_path = Path(params["train"]["model_path"])

    def get_metrics() -> dict:
        p = repo_root / metrics_path
        if not p.exists():
            raise FileNotFoundError(f"Metrics file not found: {p}")
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_model_hash() -> str:
        p = repo_root / model_path
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: {p}")
        return get_file_hash(p)

    try:
        # 1) Run pipeline from current state (e.g. after make repro once)
        run_cmd(["dvc", "repro"], cwd=repo_root)
        metrics_a = get_metrics()
        hash_a = get_model_hash()

        # 2) Re-run all stages with --force
        run_cmd(["dvc", "repro", "--force"], cwd=repo_root)
        metrics_b = get_metrics()
        hash_b = get_model_hash()

        # 3) Assert exact match
        if metrics_a != metrics_b:
            print("REPRODUCIBILITY CHECK FAILED: metrics differ between runs.", file=sys.stderr)
            print("First run:", json.dumps(metrics_a, indent=2), file=sys.stderr)
            print("Second run (after dvc repro --force):", json.dumps(metrics_b, indent=2), file=sys.stderr)
            return 1
        if hash_a != hash_b:
            print("REPRODUCIBILITY CHECK FAILED: model file hash differs between runs.", file=sys.stderr)
            print(f"First run hash:  {hash_a}", file=sys.stderr)
            print(f"Second run hash: {hash_b}", file=sys.stderr)
            return 1

        print("Reproducibility check passed: metrics and model hash match across runs.")
        return 0
    except FileNotFoundError as e:
        print(f"REPRODUCIBILITY CHECK FAILED: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"REPRODUCIBILITY CHECK FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
