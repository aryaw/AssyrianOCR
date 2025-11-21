import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
    
import psutil
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

log_path = "pipeline.log"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return 45

def check_env():
    log("INFO: Checking .env values")
    required_vars = [
        "RAW_IMAGES_PATH", "TRAIN_PATH", "VAL_PATH",
        "DETECTOR_H5", "DETECTOR_ONNX",
        "CLASSIFIER_H5", "CLASS_INDICES",
        "IMAGE_SIZE", "GRID_SIZE", "ROI_SIZE"
    ]

    missing = []
    for v in required_vars:
        if os.getenv(v) is None:
            missing.append(v)

    if missing:
        log(f"ERROR: Missing environment variables: {missing}")
        return False

    return True

def check_dataset():
    log("INFO: Checking dataset")

    raw_path = os.getenv("RAW_IMAGES_PATH")
    if not os.path.isdir(raw_path):
        log("ERROR: raw_images folder missing")
        return False

    files = os.listdir(raw_path)
    if len(files) < 5:
        log("ERROR: Dataset too small (<5 images)")
        return False

    log(f"INFO: Found {len(files)} images")
    return True

def check_ram():
    mem = psutil.virtual_memory().total / (1024 ** 3)
    log(f"INFO: RAM detected: {mem:.2f} GB")

    if mem < 3.0:
        log("WARN: Low RAM detected, training will be disabled.")
        return False
    return True

def check_temp():
    temp = get_cpu_temp()
    log(f"INFO: CPU Temp: {temp}°C")

    if temp > 80:
        log("WARN: CPU too hot — skipping training.")
        return False
    return True

def run_all_checks():
    log("=== Running pipeline pre-check ===")
    
    ok = True
    ok &= check_env()
    ok &= check_dataset()
    ok &= check_ram()
    ok &= check_temp()

    if ok:
        log("OK: Pre-check passed")
    else:
        log("FAIL: Pre-check failed")

    return ok
