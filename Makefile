PYTHON ?= python3
MPLCONFIGDIR ?= .cache/matplotlib
XDG_CACHE_HOME ?= .cache

.PHONY: install download features experiment figures summary pipeline check clean-outputs

install:
	$(PYTHON) -m pip install -r requirements.txt

download:
	$(PYTHON) scripts/download_data.py

features:
	$(PYTHON) scripts/build_features.py

experiment:
	XDG_CACHE_HOME=$(XDG_CACHE_HOME) MPLCONFIGDIR=$(MPLCONFIGDIR) $(PYTHON) scripts/run_experiment.py

figures:
	XDG_CACHE_HOME=$(XDG_CACHE_HOME) MPLCONFIGDIR=$(MPLCONFIGDIR) $(PYTHON) scripts/generate_figures.py

summary:
	$(PYTHON) scripts/export_summary.py

pipeline: download features experiment

check:
	$(PYTHON) -m compileall src scripts

clean-outputs:
	rm -f reports/figures/*.png reports/tables/*.csv reports/experiment_summary.md
