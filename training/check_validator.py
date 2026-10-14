
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    roc_auc_score,
    classification_report,
)
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

PROJECT_DIR = Path(__file__).resolve().parent.parent
VALIDATION_DIR = (
    PROJECT_DIR / "training" / "validator_split" / "validation"
)
MODEL_PATH = PROJECT_DIR / "saved_models" / "potato_validator.keras"

IMAGE_SIZE = 224
BATCH_SIZE = 32

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

val_ds = tf.keras.utils.image_dataset_from_directory(
    VALIDATION_DIR,
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False,
)

class_names = val_ds.class_names
print("Class order:", class_names)

if class_names != ["non_potato", "potato_leaf"]:
    raise ValueError(f"Unexpected class order: {class_names}")

def preprocess(images, labels):
    return preprocess_input(tf.cast(images, tf.float32)), labels

val_ds = val_ds.map(preprocess)

model = tf.keras.models.load_model(MODEL_PATH)

y_true = np.concatenate([
    labels.numpy().reshape(-1) for _, labels in val_ds
]).astype(int)

probabilities = model.predict(val_ds, verbose=1).reshape(-1)
y_pred = (probabilities >= 0.5).astype(int)

print("\nValidation samples:", len(y_true))
print("Actual label counts:", np.bincount(y_true, minlength=2))
print("Predicted label counts:", np.bincount(y_pred, minlength=2))
print("Accuracy:", accuracy_score(y_true, y_pred))
print("Confusion matrix:\n", confusion_matrix(
    y_true, y_pred, labels=[0, 1]
))
print("\nClassification report:")
print(classification_report(
    y_true,
    y_pred,
    labels=[0, 1],
    target_names=class_names,
    zero_division=0,
))
print("ROC-AUC:", roc_auc_score(y_true, probabilities))
print(
    "Probability range:",
    float(probabilities.min()),
    "to",
    float(probabilities.max()),
)
