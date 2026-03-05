# Reproducible ML Training Pipeline

Fully reproducible ML pipeline using **Git** (code), **DVC** (data and artifacts), and **YAML** configs. One command reproduces the same metrics and model artifact hash.

- **Stack:** Python 3.11, scikit-learn, DVC, `params.yaml`
- **Pipeline:** data → preprocess → train → evaluate (all in `dvc.yaml`)
- **CI:** GitHub Actions runs a reproducibility check on every PR; workflow fails if results differ.

---

## One-command reproduction

From a fresh clone:

```bash
git clone <your-repo-url> mlops-training && cd mlops-training
make setup
make repro
```

Then verify reproducibility:

```bash
make repro-check
```

`make repro-check` runs the pipeline, then `dvc repro --force`, and **asserts that metrics and model file hash are identical**. If not, it prints a clear failure message and exits with code 1.

---

## Step-by-step setup

### 1. Clone and enter the repo

```bash
git clone <your-repo-url> mlops-training
cd mlops-training
```

### 2. Initialise Git (if not already a repo)

```bash
git init
```

### 3. Initialise DVC and optional remote

```bash
# Required: initialise DVC
dvc init

# Optional: add a remote (not committed; .dvc/config is in .gitignore)
mkdir -p ../dvc-remote
dvc remote add myremote ../dvc-remote

# Or use S3 / GDrive (see "DVC remote" section below)
# dvc remote add myremote s3://mybucket/dvc-store
# dvc remote add myremote gdrive://my-drive/dvc
```

### 4. Install dependencies and run the pipeline

```bash
make setup
make repro
```

This generates:

- `data/raw.csv`, `data/train.csv`, `data/test.csv`
- `models/model.joblib`
- `artefacts/preds.csv`
- `metrics.json`

### 5. Track outputs with DVC and push (optional)

After the first `make repro`, track and push if you use a remote:

```bash
# DVC already tracks pipeline outs via dvc.yaml; to push cache to remote:
dvc push

# Commit DVC files so others can pull
git add dvc.lock dvc.yaml params.yaml .gitignore
git commit -m "Add DVC pipeline and lockfile"
```

### 6. Pull data and artifacts (on another machine or CI)

```bash
git pull
dvc pull
make repro   # or only run missing stages
```

---

## Repo layout

```
├── .github/workflows/repro.yml   # CI: runs make repro-check on PR
├── .dvcignore
├── .gitignore
├── Makefile                      # setup, repro, repro-check, clean
├── README.md
├── params.yaml                   # All tunables (seed, paths, hyperparams)
├── dvc.yaml                      # Pipeline stages
├── requirements.txt
├── repro_check.py                # Asserts metrics + model hash match across two runs
├── configs/
├── src/
│   ├── data.py                   # Load sklearn dataset → data/raw.csv
│   ├── preprocess.py             # Train/test split → data/train.csv, test.csv
│   ├── train.py                  # Fit model → models/model.joblib
│   ├── evaluate.py               # Metrics + preds → metrics.json, artefacts/preds.csv
│   └── utils.py                  # Seed, config, hashing
├── data/                         # DVC-tracked
├── models/                       # DVC-tracked
└── artefacts/                    # DVC-tracked
```

---

## Makefile targets

| Target        | Description |
|---------------|-------------|
| `make setup`  | Install pip, `requirements.txt`, and DVC |
| `make repro`  | Run full pipeline (`dvc repro`) |
| `make repro-check` | Run pipeline, then `dvc repro --force`, assert metrics and model hash identical |
| `make clean`  | Remove pipeline outputs and optional DVC cache (for a clean re-run) |

---

## DVC remote: local vs S3 / GDrive

**`.dvc/config` is in `.gitignore`** so your local remote path (or credentials) is never committed. After cloning, if you need a remote, add it yourself:

```bash
# Local folder (e.g. on the same machine)
mkdir -p ../dvc-remote
dvc remote add myremote ../dvc-remote
```

- **Local:** `dvc remote add myremote ../dvc-remote` then `dvc push` / `dvc pull`. No extra setup.
- **S3:** Create a bucket, then e.g. `dvc remote add myremote s3://bucket/dvc-store`. Configure credentials via env vars or `aws configure`.
- **GDrive:** `dvc remote add myremote gdrive://<folder-id>`. Use `dvc remote modify myremote gdrive_use_service_account true` and credentials if needed.

After adding a remote, run `dvc push` to upload, and on other clones run `dvc remote add` (and optionally `dvc pull`) before `make repro` if you rely on cached data.

---

## How CI verifies reproducibility

1. **Checkout** the PR branch.
2. **Set up Python 3.11** and install `requirements.txt` and DVC.
3. **Run `make repro-check`**, which:
   - Runs `dvc repro` (full pipeline from current state).
   - Records `metrics.json` and the SHA-256 hash of `models/model.joblib`.
   - Runs `dvc repro --force` (re-runs all stages).
   - Compares metrics and model hash; **fails the workflow if any difference**.

So CI ensures that two consecutive full runs produce **exactly** the same metrics and model file.

---

## Exact terminal commands (summary)

```bash
# Initialise and first run
git clone <repo> mlops-training && cd mlops-training
git init
dvc init
mkdir -p ../dvc-remote && dvc remote add myremote ../dvc-remote
make setup
make repro
make repro-check

# Optional: push DVC data and commit
dvc push
git add .
git commit -m "Pipeline and DVC setup"
```

---

## Windows

If `make` is not available, use:

```powershell
pip install -r requirements.txt
pip install dvc
dvc repro
python repro_check.py
```

---

## Checklist

- [ ] `make setup` completes without errors
- [ ] `make repro` produces `data/`, `models/model.joblib`, `artefacts/preds.csv`, `metrics.json`
- [ ] `make repro-check` prints "Reproducibility check passed" and exits 0
- [ ] Changing `seed` in `params.yaml` and running `make repro` changes metrics
- [ ] CI workflow runs on PR and passes when the pipeline is unchanged
