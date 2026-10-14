
from pathlib import Path
import tensorflow as tf

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "training" / "validator_dataset"

for subset in ("training", "validation"):
    ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.20,
        subset=subset,
        seed=42,
        image_size=(224, 224),
        batch_size=32,
        label_mode="binary",
        shuffle=False,
    )

    counts = [0, 0]

    for _, labels in ds:
        for label in labels.numpy().reshape(-1).astype(int):
            counts[label] += 1

    print(f"\n{subset}:")
    print("Class names:", ds.class_names)
    print("non_potato:", counts[0])
    print("potato_leaf:", counts[1])
