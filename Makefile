# One-command reproduction: make setup && make repro
# Reproducibility verification: make repro-check

PYTHON ?= python
PIP ?= pip

.PHONY: setup repro repro-check clean

# Install Python deps and ensure DVC is available
setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install dvc
	@echo "Setup done. Run 'make repro' to reproduce the pipeline."

# Run full DVC pipeline (data -> preprocess -> train -> evaluate)
repro:
	dvc repro

# Verify reproducibility: run pipeline, then repro --force, assert metrics and model hash match
repro-check: repro
	$(PYTHON) repro_check.py

# Remove pipeline outputs and DVC cache (optional; use before a clean re-run)
clean:
	dvc destroy --force || true
	rm -rf data/raw.csv data/train.csv data/test.csv
	rm -rf models/model.joblib
	rm -rf artefacts/preds.csv
	rm -f metrics.json
	@echo "Clean done. Run 'dvc repro' to regenerate."
