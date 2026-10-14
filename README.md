# PotatoGuard AI ≡ƒÑö

**AI-powered potato leaf validation and disease classification**

PotatoGuard AI is a computer-vision application that first checks whether an image appears to show a potato leaf and then predicts one of three classes: **Early Blight**, **Late Blight**, or **Healthy**. It combines a React frontend, FastAPI backend, and TensorFlow/Keras models.

> **Note:** The metrics below are results from the project's current local test/validation splits. They are not guarantees of real-world performance.

## Features

- Potato-leaf validation using a binary classifier.
- Three-class potato disease classification.
- Two-stage workflow: validate the image, then classify accepted potato-leaf images.
- React web interface with Material UI.
- FastAPI REST backend.
- TensorFlow/Keras inference using saved `.keras` models.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| UI | Material UI |
| Backend | Python, FastAPI |
| Model framework | TensorFlow / Keras |
| API server | Uvicorn |
| Model format | `.keras` |

## How It Works

1. The user uploads an image through the frontend.
2. The validator predicts whether it is a potato leaf.
3. If it passes validation, the disease classifier predicts Early Blight, Late Blight, or Healthy.
4. The backend returns the prediction to the frontend.

## Models

### Potato-leaf validator

- **File:** `saved_models/potato_validator.keras`
- **Classes:** `non_potato`, `potato_leaf`
- **Input size:** `224 ├ù 224`
- **Preprocessing:** `tf.keras.applications.mobilenet_v2.preprocess_input`
- **Application threshold:** `0.80`

### Disease classifier

- **File:** `saved_models/my_model_v1.keras`
- **Classes:** Early Blight, Late Blight, Healthy
- **Input size:** `256 ├ù 256`
- **Preprocessing:** The model includes an internal rescaling layer (`1./255`).

Keep both model files at the paths expected by the backend.

## Evaluation Results

### Disease classifier

Evaluated on **431 test images**.

| Metric | Result |
|---|---:|
| Accuracy | **97.68%** |
| Macro F1-score | **97.04%** |
| Correct predictions | 421 / 431 |

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Early Blight | 97.54% | 99.00% | 98.26% | 200 |
| Late Blight | 98.97% | 96.00% | 97.46% | 200 |
| Healthy | 91.18% | 100.00% | 95.38% | 31 |

The Healthy class has fewer test examples than the disease classes, so its score should be interpreted with that limitation in mind.

### Potato-leaf validator

Evaluated on **894 validation images** after removing two exact duplicate validation copies.

| Metric | Result |
|---|---:|
| Accuracy at threshold 0.80 | **99.78%** |
| Macro F1-score at threshold 0.80 | **99.78%** |
| ROC-AUC | **1.000** |
| Correct predictions at threshold 0.80 | 892 / 894 |

Validation class counts: 464 `non_potato` and 430 `potato_leaf`.

**Evaluation caveat:** Exact SHA-256 checks found no exact duplicates between the disease classifier's training, validation, and test splits. Two exact duplicate groups were found across the validator's training and validation splits; the validation copies were moved to `training/validator_split/duplicate_quarantine` before this evaluation. SHA-256 does not detect resized, recompressed, or visually similar images. Treat these scores as local split results, not independent real-world performance guarantees.

## Repository Structure

The layout can vary slightly by local setup. Main project areas include:

```text
PotatoGuard-AI/
Γö£ΓöÇΓöÇ api/
Γöé   ΓööΓöÇΓöÇ main.py
Γö£ΓöÇΓöÇ saved_models/
Γöé   Γö£ΓöÇΓöÇ my_model_v1.keras
Γöé   ΓööΓöÇΓöÇ potato_validator.keras
Γö£ΓöÇΓöÇ training/
Γöé   Γö£ΓöÇΓöÇ dataset/
Γöé   Γö£ΓöÇΓöÇ validator_dataset/
Γöé   Γö£ΓöÇΓöÇ validator_split/
Γöé   Γö£ΓöÇΓöÇ evaluate_disease_model.py
Γöé   Γö£ΓöÇΓöÇ evaluate_validator.py
Γöé   ΓööΓöÇΓöÇ check_within_model_duplicates.py
Γö£ΓöÇΓöÇ frontend/
Γö£ΓöÇΓöÇ .gitignore
ΓööΓöÇΓöÇ README.md
```

Datasets, virtual environments, caches, and temporary files should remain excluded from Git where appropriate. The saved model files are required for inference unless the backend is configured to load them from elsewhere.

## Local Setup

### Prerequisites

- Python compatible with the project's TensorFlow version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/MohammedRiyan22/PotatoGuard-AI.git
cd PotatoGuard-AI
```

### 2. Create and activate the Python environment

On Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies using the requirements file included with your checkout:

```powershell
pip install -r requirements.txt
```

If the backend requirements file is stored in a subdirectory, use that file's path instead. TensorFlow compatibility depends on the Python version and installed dependencies.

### 3. Start the backend

From the repository root, with the virtual environment activated:

```powershell
python -m uvicorn api.main:app --reload
```

Use the module path defined by your checkout if the entry point differs. When running, FastAPI commonly provides interactive documentation at `http://127.0.0.1:8000/docs`.

### 4. Start the frontend

In a second terminal, enter the directory containing the frontend's `package.json` (commonly `frontend/`) and run:

```powershell
npm install
npm start
```

If the frontend is in the repository root, run these commands there instead.

## Evaluation Scripts

Run from the repository root with the project's virtual environment activated:

```powershell
python .\training\evaluate_disease_model.py
python .\training\evaluate_validator.py
python .\training\check_within_model_duplicates.py
```

These scripts require the corresponding local datasets and saved models. The datasets may not be included in the GitHub repository.

## Important Notes

- Predictions are model outputs, not a definitive agricultural diagnosis.
- Lighting, image quality, background, disease stage, and differences between training data and real-world photos can affect results.
- For stronger evidence of generalization, evaluate on representative images that were not used in training, model selection, or threshold tuning.
- Confirm dataset redistribution rights before publishing datasets.

## Future Improvements

- Evaluate on a separately collected real-world image set.
- Check perceptual/near-duplicate images in addition to exact file hashes.
- Add clearer prediction explanations and confidence visualization.
- Improve API input validation and error handling.
- Document exact dependency versions and add automated tests.

## Author

**Mohammed Riyan Ur Raheman**

GitHub: [@MohammedRiyan22](https://github.com/MohammedRiyan22)

## Repository

[PotatoGuard AI on GitHub](https://github.com/MohammedRiyan22/PotatoGuard-AI)
