
from pathlib import Path
import random
import shutil

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "training" / "validator_dataset"
SPLIT_DIR = PROJECT_DIR / "training" / "validator_split"

SEED = 42
VALIDATION_FRACTION = 0.20
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

random.seed(SEED)

# Refuse to overwrite an existing split.
if SPLIT_DIR.exists() and any(SPLIT_DIR.iterdir()):
    raise FileExistsError(
        f"{SPLIT_DIR} is not empty. Inspect it before rerunning this script."
    )

for split in ("train", "validation"):
    for class_name in ("non_potato", "potato_leaf"):
        (SPLIT_DIR / split / class_name).mkdir(
            parents=True, exist_ok=True
        )

for class_name in ("non_potato", "potato_leaf"):
    source = DATA_DIR / class_name

    files = [
        p for p in source.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    ]

    random.shuffle(files)

    val_count = max(1, round(len(files) * VALIDATION_FRACTION))
    validation_files = files[:val_count]
    training_files = files[val_count:]

    for file in training_files:
        shutil.copy2(file, SPLIT_DIR / "train" / class_name / file.name)

    for file in validation_files:
        shutil.copy2(file, SPLIT_DIR / "validation" / class_name / file.name)

    print(
        f"{class_name}: {len(training_files)} training, "
        f"{len(validation_files)} validation"
    )

print(f"\nPrepared split at: {SPLIT_DIR}")
print("Original validator_dataset files were not modified.")
