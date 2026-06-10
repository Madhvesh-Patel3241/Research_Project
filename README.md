# Research Project

Brief overview: research code and datasets for Ethereum mempool attack detection and experiments.

**Top-level structure (overview of subfolders)**

- **Dataset/**: data-processing scripts and CSV datasets (merge, augment, balance, tests).
- **data/**: binary numpy data arrays for training/testing and preprocessed inputs.
- **models/**: trained model artifacts (e.g. `1d_cnn.h5`, `bilstm.h5`, `deep_mlp.h5`, `transformer.h5`).
- **ethereum-mempool-detection/**: Jupyter notebooks for EDA, classical ML, deep learning, and final comparisons.
- **Ensemble/**: notebooks and helpers for ensemble learning experiments and results.
- **Real_World_Test/**: scripts, validators, and experiment outputs for real-world validation.
- **results/**: generated result CSVs and summaries from experiments.
- **Output_Generating_Dataset/**: utilities and outputs used to generate datasets for training.

**Notable top-level scripts**

- `attack_generator.py`, `attack_new_script.py`: tools to synthesize or simulate attack transactions.
- `detector.py`, `detector_new_script.py`: main detection scripts (entry points for running models).
- `merge_dataset_ script.py`, `merge_dataset.py`: dataset merging utilities.

**Quick start**

1. Prepare data in `Dataset/` or use preprocessed arrays in `data/`.
2. Run a detector script, for example:

```
python detector.py
```

Or run real-world validation:

```
python Real_World_Test/real_world_test.py
```

Refer to notebooks in `ethereum-mempool-detection/` for experiment details and preprocessing steps.

**Notes**

- This README is intentionally for the repository root only; see individual subfolders for more detailed READMEs or usage notes.
- Python 3.8+ is recommended; install project dependencies as needed.
