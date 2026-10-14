# PotatoGuard AI --- Smart Crop Health

PotatoGuard AI is a web application that analyzes an uploaded
potato-leaf image and predicts whether it shows **Early Blight**, **Late
Blight**, or is **Healthy**. A separate image-validation model checks
whether the uploaded image is likely to be a potato leaf before disease
classification.

> **Note:** Predictions are model outputs, not a confirmed plant-health
> diagnosis. Results may be unreliable for images outside the models'
> training data.

## Features

-   Upload a potato-leaf image from the browser.
-   Preview the selected image before or during analysis.
-   Validate the image as a likely potato leaf before classification.
-   Predict one of three classes: Early Blight, Late Blight, or Healthy.
-   Display the disease model's confidence and potato-leaf probability.
-   Reject unsupported or non-potato images with a clear message.
-   Provide a responsive React interface with a custom green-leaf
    favicon.
-   Expose the prediction service through a FastAPI REST API.

## Technology Stack

**Frontend** - React (Create React App) - Material-UI - Axios

**Backend and Machine Learning** - Python - FastAPI and Uvicorn -
TensorFlow / Keras - Pillow and NumPy - MobileNetV2 preprocessing for
the potato-leaf validator

## Project Structure

``` text
potato-disease/
├── api/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── favicon.png
│   │   └── index.html
│   ├── src/
│   │   └── home.js
│   ├── .env
│   └── package.json
├── saved_models/
│   ├── my_model_v1.keras
│   └── potato_validator.keras
├── training/
├── start-project.ps1
└── README.md
```

Some training and supporting files may be present locally but are not
required to be committed to GitHub. Keep the model paths in sync with
the files available in your checkout.

## How It Works

1.  The user selects an image in the React frontend.
2.  The frontend sends the image as multipart form data to the FastAPI
    `/predict` endpoint.
3.  The validator estimates whether the image is a potato leaf.
4.  If the image passes the configured validation threshold, the disease
    model predicts Early Blight, Late Blight, or Healthy.
5.  The frontend displays the predicted class, confidence score, and
    potato-leaf probability.

The validator currently uses a threshold of `0.80`. This is a
configurable application setting, not a guarantee that every real-world
image will be correctly accepted or rejected.

## Prerequisites

Install the following before running the project:

-   Python compatible with the installed TensorFlow version (the project
    was set up using a Python 3.10 virtual environment)
-   Node.js and npm
-   Git (optional, for cloning and version control)

## Setup

### 1. Get the project

Clone your repository, or open your existing project folder:

``` powershell
cd C:\potato-disease
```

### 2. Set up the Python environment

If the project already has its `.venv` environment, activate it:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If you need to create the environment, use Python 3.10 if available:

``` powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

``` powershell
python -m pip install --upgrade pip
pip install -r api\requirements.txt
```

Make sure these model files exist before starting the API:

``` text
saved_models\my_model_v1.keras
saved_models\potato_validator.keras
```

### 3. Configure the frontend

Open `frontend\.env` and set the API URL:

``` dotenv
REACT_APP_API_URL=http://127.0.0.1:8000/predict
```

The frontend also has this default API URL in its code. Keep the `.env`
value aligned with the backend address if you change the port or host.

Install frontend dependencies:

``` powershell
cd frontend
npm install
```

Return to the project root before using the startup script:

``` powershell
cd ..
```

## Run the Application

### Recommended: start both services

From the project root (`C:\potato-disease`), run:

``` powershell
.\start-project.ps1
```

The script opens the FastAPI backend in a separate PowerShell window and
starts the React frontend in the current terminal. Keep both windows
open while using the application.

If PowerShell blocks the script because of the local execution policy,
run it for the current command with:

``` powershell
powershell -ExecutionPolicy Bypass -File .\start-project.ps1
```

### Start services manually

Start the backend in one terminal from the project root:

``` powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend in a second terminal:

``` powershell
cd frontend
npm start
```

## Local URLs

  Service                       URL
  ----------------------------- -------------------------------
  React frontend                http://localhost:3000
  FastAPI root                  http://127.0.0.1:8000
  API health check              http://127.0.0.1:8000/ping
  Interactive API docs          http://127.0.0.1:8000/docs
  Disease prediction endpoint   http://127.0.0.1:8000/predict

## Prediction API

### `POST /predict`

Send an image using `multipart/form-data` with the field name `file`.

Example using `curl`:

``` bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -F "file=@path/to/potato_leaf.jpg"
```

A successful response has this structure:

``` json
{
  "class": "Early Blight",
  "confidence": 0.99,
  "potato_leaf_probability": 0.99
}
```

The values above are illustrative examples, not a promise of model
performance. The API may return an HTTP 400 response when the image is
not confidently identified as a potato leaf, and may reject unsupported
files or images that exceed the upload limit.

## Model Notes

-   The disease classifier expects RGB images resized to `256 × 256`.
-   The disease model includes its own rescaling layer; the API supplies
    pixel values in the expected `0–255` range.
-   The validator expects `224 × 224` images and uses MobileNetV2
    `preprocess_input`.
-   Disease classes are mapped to: `Early Blight`, `Late Blight`, and
    `Healthy`.
-   The validator's configured acceptance threshold is `0.80`.

Model quality depends on the training data and evaluation method. Test
with varied real-world images before relying on predictions.

## Git and Repository Hygiene

Before pushing to GitHub:

-   Do **not** commit `.venv/`, `frontend/node_modules/`, caches, local
    logs, or environment-specific secrets.
-   Keep local `.env` files out of Git if they contain machine-specific
    configuration or secrets. For this project, the API URL is not a
    secret, but a `.env.example` can document the required variable.
-   Check the size of `.keras` model files before committing. If they
    exceed GitHub's file-size limits or make the repository
    unnecessarily large, use Git LFS or publish the model artifacts
    separately and document how to obtain them.
-   Include the custom favicon at `frontend/public/favicon.png`.
-   Keep `start-project.ps1` and this README updated when startup
    commands or paths change.

A useful `.gitignore` baseline for this project is:

``` gitignore
# Python
.venv/
__pycache__/
*.py[cod]
.pytest_cache/

# Node / React
frontend/node_modules/
frontend/build/
frontend/.env

# Local files and logs
*.log
.DS_Store
Thumbs.db
```

If the model files are required for others to run the application,
decide explicitly whether to track them in Git, use Git LFS, or provide
a documented download location. Do not ignore them without making them
available another way.

## Troubleshooting

**Frontend cannot connect to the API** - Confirm the backend is running
at `http://127.0.0.1:8000`. - Open `http://127.0.0.1:8000/ping` to check
the API. - Confirm `frontend/.env` contains the correct
`REACT_APP_API_URL`. - Restart `npm start` after changing `.env`.

**Model file not found** - Confirm both model files exist in
`saved_models/`. - Run the backend from the project root so the
configured relative paths resolve as expected.

**Favicon does not update** - Confirm `frontend/public/favicon.png`
exists and the icon link in `frontend/public/index.html` points to
`/favicon.png` using `%PUBLIC_URL%`. - Refresh with `Ctrl + Shift + R`,
or open the site in a new browser tab.

**Port already in use** - Stop the existing process using the port
before starting another instance.

## License

Add a license before distributing this project publicly. Until a license
is added, do not assume others have permission to reuse the source code
or model artifacts.
