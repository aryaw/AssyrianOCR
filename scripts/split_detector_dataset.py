import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
    
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

DETECTOR_ROOT = os.getenv("DETECTOR_ROOT", "data/detector")
TRAIN_PATH = os.getenv("TRAIN_PATH", "data/detector/train")
VAL_PATH = os.getenv("VAL_PATH", "data/detector/val")

SRC_IMAGES = os.path.join(TRAIN_PATH, "images")
SRC_ANN = os.path.join(TRAIN_PATH, "annotations.csv")

# Output dirs
TRAIN_OUT = TRAIN_PATH
VAL_OUT = VAL_PATH

def ensure_dirs():
    os.makedirs(os.path.join(TRAIN_OUT, "images"), exist_ok=True)
    os.makedirs(os.path.join(VAL_OUT, "images"), exist_ok=True)

def split_dataset():
    if not os.path.exists(SRC_ANN):
        print("[ERROR] annotations.csv not found!")
        return

    df = pd.read_csv(SRC_ANN)
    if "filename" not in df.columns:
        print("[ERROR] CSV missing filename column!")
        return

    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    # Save split annotations
    train_df.to_csv(os.path.join(TRAIN_OUT, "annotations.csv"), index=False)
    val_df.to_csv(os.path.join(VAL_OUT, "annotations.csv"), index=False)

    # Copy images
    for _, row in train_df.iterrows():
        src = os.path.join(SRC_IMAGES, row["filename"])
        dst = os.path.join(TRAIN_OUT, "images", row["filename"])
        if os.path.exists(src):
            shutil.copy(src, dst)

    for _, row in val_df.iterrows():
        src = os.path.join(SRC_IMAGES, row["filename"])
        dst = os.path.join(VAL_OUT, "images", row["filename"])
        if os.path.exists(src):
            shutil.copy(src, dst)

    print(f"[OK] Train/Val split completed")
    print(f"Train: {len(train_df)} images")
    print(f"Val:   {len(val_df)} images")


if __name__ == "__main__":
    ensure_dirs()
    split_dataset()
