
from pathlib import Path
from io import BytesIO
import logging

import numpy as np
import tensorflow as tf
import uvicorn

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


# ==================================================
# 1. CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
MODEL_DIR = PROJECT_DIR / "saved_models"

DISEASE_MODEL_PATH = MODEL_DIR / "my_model_v1.keras"
VALIDATOR_MODEL_PATH = MODEL_DIR / "potato_validator.keras"

# Disease model class order
CLASS_NAMES = [
    "Early Blight",
    "Late Blight",
    "Healthy",
]

VALIDATOR_IMAGE_SIZE = 224

MAX_FILE_SIZE = 10 * 1024 * 1024

# Provisional threshold; tune using independent test data.
POTATO_THRESHOLD = 0.80

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("potato_disease_api")


# ==================================================
# 2. CREATE FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Potato Disease Detection API",
    description=(
        "Two-stage potato disease detection system. "
        "First validates whether the uploaded image "
        "resembles a potato leaf, then classifies "
        "Early Blight, Late Blight, or Healthy."
    ),
    version="2.1.0",
)


# ==================================================
# 3. CORS CONFIGURATION
# ==================================================

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# 4. LOAD TRAINED MODELS
# ==================================================

for model_path in [
    DISEASE_MODEL_PATH,
    VALIDATOR_MODEL_PATH,
]:
    if not model_path.is_file():
        raise FileNotFoundError(
            f"Required model not found: {model_path}"
        )


logger.info("Loading disease classification model...")

DISEASE_MODEL = tf.keras.models.load_model(
    DISEASE_MODEL_PATH,
    compile=False,
)

logger.info("Loading potato leaf validator...")

VALIDATOR_MODEL = tf.keras.models.load_model(
    VALIDATOR_MODEL_PATH,
    compile=False,
)

logger.info("Both models loaded successfully.")

logger.info(
    "Disease model input: %s",
    DISEASE_MODEL.input_shape,
)

logger.info(
    "Disease model output: %s",
    DISEASE_MODEL.output_shape,
)

logger.info(
    "Validator model input: %s",
    VALIDATOR_MODEL.input_shape,
)

logger.info(
    "Validator model output: %s",
    VALIDATOR_MODEL.output_shape,
)


# ==================================================
# 5. VERIFY MODEL SHAPES
# ==================================================

if DISEASE_MODEL.input_shape[1:] != (256, 256, 3):
    raise RuntimeError(
        "Unexpected disease model input shape."
    )

if DISEASE_MODEL.output_shape[-1] != len(CLASS_NAMES):
    raise RuntimeError(
        "Disease model output does not match class count."
    )

if VALIDATOR_MODEL.input_shape[1:] != (224, 224, 3):
    raise RuntimeError(
        "Unexpected validator model input shape."
    )

if VALIDATOR_MODEL.output_shape[-1] != 1:
    raise RuntimeError(
        "Validator must produce one probability."
    )


# ==================================================
# 6. READ AND VALIDATE IMAGE
# ==================================================

def read_image(data: bytes) -> np.ndarray:
    """
    Read uploaded image bytes and return an RGB NumPy array.

    Output:
        shape = (height, width, 3)
        dtype = uint8
        range = 0 to 255
    """

    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()

        with Image.open(BytesIO(data)) as img:
            rgb_image = img.convert("RGB")
            image_array = np.asarray(
                rgb_image,
                dtype=np.uint8,
            )

        return image_array

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image. Please upload a valid "
                "JPG, JPEG, PNG, WEBP, or BMP image."
            ),
        ) from exc


# ==================================================
# 7. POTATO LEAF VALIDATION
# ==================================================

def validate_potato_leaf(image: np.ndarray) -> float:
    """
    Validate whether an image resembles a potato leaf.

    Model:
        potato_validator.keras

    Input:
        224 x 224 RGB

    Preprocessing:
        MobileNetV2 preprocess_input
        Pixel range: [-1, 1]

    Output:
        Potato-leaf probability between 0 and 1.
    """

    resized = tf.image.resize(
        image,
        (
            VALIDATOR_IMAGE_SIZE,
            VALIDATOR_IMAGE_SIZE,
        ),
    )

    resized = tf.cast(
        resized,
        tf.float32,
    )

    processed = preprocess_input(resized)

    batch = tf.expand_dims(
        processed,
        axis=0,
    )

    prediction = VALIDATOR_MODEL.predict(
        batch,
        verbose=0,
    )

    output = np.asarray(prediction)

    if output.size != 1:
        raise RuntimeError(
            "Unexpected validator output shape."
        )

    probability = float(
        output.reshape(-1)[0]
    )

    if (
        not np.isfinite(probability)
        or not 0.0 <= probability <= 1.0
    ):
        raise RuntimeError(
            "Invalid validator probability."
        )

    return probability


# ==================================================
# 8. DISEASE IMAGE PREPROCESSING
# ==================================================

def prepare_disease_image(
    image: np.ndarray,
) -> np.ndarray:
    """
    Prepare an RGB NumPy array for the disease model.

    IMPORTANT:
    The disease model already contains Rescaling(1./255).

    Therefore:
        Do NOT divide image pixels by 255 here.

    Input:
        RGB NumPy array

    Output:
        (1, 256, 256, 3)
        float32
        Pixel range: 0 to 255
    """

    input_shape = DISEASE_MODEL.input_shape

    height = input_shape[1]
    width = input_shape[2]

    if height is None or width is None:
        raise RuntimeError(
            "Disease model input size is undefined."
        )

    # Convert NumPy array into a PIL Image.
    pil_image = Image.fromarray(
        image.astype(np.uint8)
    )

    # Resize to the disease model's expected dimensions.
    pil_image = pil_image.resize(
        (width, height),
        resample=Image.Resampling.BILINEAR,
    )

    # Keep pixel values between 0 and 255.
    image_array = np.asarray(
        pil_image,
        dtype=np.float32,
    )

    # Add batch dimension.
    batch = np.expand_dims(
        image_array,
        axis=0,
    )

    return batch


# ==================================================
# 9. ROOT ENDPOINT
# ==================================================

@app.get("/")
async def root():
    return {
        "message": "Potato Disease Detection API is running.",
        "version": "2.1.0",
        "documentation": "/docs",
        "health_check": "/ping",
        "prediction_endpoint": "/predict",
    }


# ==================================================
# 10. HEALTH CHECK ENDPOINT
# ==================================================

@app.get("/ping")
async def ping():
    return {
        "message": "Potato Disease Detection API is running.",
        "disease_model_loaded": DISEASE_MODEL is not None,
        "validator_model_loaded": VALIDATOR_MODEL is not None,
    }


# ==================================================
# 11. MODEL INFORMATION ENDPOINT
# ==================================================

@app.get("/model-info")
async def model_info():
    return {
        "disease_model": DISEASE_MODEL_PATH.name,
        "validator_model": VALIDATOR_MODEL_PATH.name,
        "disease_classes": CLASS_NAMES,
        "potato_acceptance_threshold": POTATO_THRESHOLD,
        "disease_input_shape": [256, 256, 3],
        "validator_input_shape": [224, 224, 3],
    }


# ==================================================
# 12. PREDICTION ENDPOINT
# ==================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
):
    try:

        # ------------------------------------------
        # STEP 1: CHECK UPLOADED FILE TYPE
        # ------------------------------------------

        if (
            file.content_type
            and not file.content_type.startswith("image/")
        ):
            raise HTTPException(
                status_code=400,
                detail="Please upload an image file.",
            )

        # ------------------------------------------
        # STEP 2: READ FILE WITH SIZE LIMIT
        # ------------------------------------------

        file_bytes = await file.read(
            MAX_FILE_SIZE + 1
        )

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Image exceeds the 10 MB upload limit.",
            )

        # ------------------------------------------
        # STEP 3: DECODE IMAGE
        # ------------------------------------------

        image = read_image(file_bytes)

        logger.info(
            "Uploaded image shape: %s",
            image.shape,
        )

        # ------------------------------------------
        # STEP 4: VALIDATE POTATO LEAF
        # ------------------------------------------

        potato_probability = validate_potato_leaf(
            image
        )

        logger.info(
            "Potato leaf probability: %.4f",
            potato_probability,
        )

        if potato_probability < POTATO_THRESHOLD:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This image could not be confidently "
                    "identified as a potato leaf. "
                    "Please upload only potato leaf image."
                ),
            )

        # ------------------------------------------
        # STEP 5: PREPARE DISEASE MODEL INPUT
        # ------------------------------------------

        disease_batch = prepare_disease_image(
            image
        )

        logger.info(
            "Disease model batch shape: %s",
            disease_batch.shape,
        )

        # ------------------------------------------
        # STEP 6: RUN DISEASE PREDICTION
        # ------------------------------------------

        prediction = DISEASE_MODEL.predict(
            disease_batch,
            verbose=0,
        )

        output = np.asarray(prediction)

        if (
            output.ndim != 2
            or output.shape != (1, len(CLASS_NAMES))
        ):
            raise RuntimeError(
                "Unexpected disease model output shape."
            )

        scores = output[0]

        if not np.all(np.isfinite(scores)):
            raise RuntimeError(
                "Disease model returned invalid scores."
            )

        # ------------------------------------------
        # STEP 7: GET PREDICTED CLASS
        # ------------------------------------------

        predicted_index = int(
            np.argmax(scores)
        )

        predicted_class = CLASS_NAMES[
            predicted_index
        ]

        confidence = float(
            scores[predicted_index]
        )

        logger.info(
            "Prediction: %s | Confidence: %.4f",
            predicted_class,
            confidence,
        )

        # ------------------------------------------
        # STEP 8: RETURN PREDICTION
        # ------------------------------------------

        return {
            "class": predicted_class,
            "confidence": confidence,
            "potato_leaf_probability": potato_probability,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error during prediction."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed. "
                "Check the backend terminal logs."
            ),
        )

    finally:
        await file.close()


# ==================================================
# 13. START SERVER
# ==================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
