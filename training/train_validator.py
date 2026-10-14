
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "training" / "validator_dataset"
MODEL_DIR = PROJECT_DIR / "saved_models"
MODEL_PATH = MODEL_DIR / "potato_validator.keras"

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
SEED = 42

# Create output directory before training/checkpointing.
MODEL_DIR.mkdir(parents=True, exist_ok=True)
tf.keras.utils.set_random_seed(SEED)

# --------------------------------------------------
# Validate dataset folders
# --------------------------------------------------

for folder_name in ("non_potato", "potato_leaf"):
    folder = DATA_DIR / folder_name

    if not folder.is_dir():
        raise FileNotFoundError(f"Missing folder: {folder}")

    image_count = sum(
        1 for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".bmp", ".webp"
        }
    )

    if image_count == 0:
        raise ValueError(f"No supported images found in {folder}")

    print(f"{folder_name}: {image_count} images")

# --------------------------------------------------
# Load datasets
# --------------------------------------------------


SPLIT_DIR = PROJECT_DIR / "training" / "validator_split"

train_ds = tf.keras.utils.image_dataset_from_directory(
    SPLIT_DIR / "train",
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=True,
    seed=SEED,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    SPLIT_DIR / "validation",
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False,
)

print("Class names:", train_ds.class_names)
print("Validation classes:", val_ds.class_names)

if train_ds.class_names != ["non_potato", "potato_leaf"]:
    raise ValueError(f"Unexpected training classes: {train_ds.class_names}")

if val_ds.class_names != ["non_potato", "potato_leaf"]:
    raise ValueError(f"Unexpected validation classes: {val_ds.class_names}")


# --------------------------------------------------
# Preprocessing
# --------------------------------------------------

AUTOTUNE = tf.data.AUTOTUNE

def preprocess_dataset(images, labels):
    images = preprocess_input(tf.cast(images, tf.float32))
    return images, labels

train_ds = train_ds.map(
    preprocess_dataset,
    num_parallel_calls=AUTOTUNE,
).prefetch(AUTOTUNE)

val_ds = val_ds.map(
    preprocess_dataset,
    num_parallel_calls=AUTOTUNE,
).prefetch(AUTOTUNE)

# --------------------------------------------------
# Build MobileNetV2 binary classifier
# --------------------------------------------------

base_model = MobileNetV2(
    input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
    include_top=False,
    weights="imagenet",
)

base_model.trainable = False

inputs = layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.25)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)

model = models.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=[
        "accuracy",
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
        tf.keras.metrics.AUC(name="auc"),
    ],
)

model.summary()

# --------------------------------------------------
# Callbacks
# --------------------------------------------------

callbacks = [
    tf.keras.callbacks.ModelCheckpoint(
        filepath=str(MODEL_PATH),
        monitor="val_auc",
        mode="max",
        save_best_only=True,
        verbose=1,
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1,
    ),
]

# --------------------------------------------------
# Train
# --------------------------------------------------

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks,
)

# --------------------------------------------------
# Evaluate the best saved checkpoint
# --------------------------------------------------

if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"Training did not produce the expected model: {MODEL_PATH}"
    )

best_model = tf.keras.models.load_model(MODEL_PATH)

print("\nBest checkpoint evaluation on validation data:")
results = best_model.evaluate(val_ds, return_dict=True)

for metric, value in results.items():
    print(f"{metric}: {value:.4f}")

print("\nValidator training complete.")
print("Saved model:", MODEL_PATH)
print("Class order: non_potato=0, potato_leaf=1")
