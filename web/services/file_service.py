import os, uuid
from pathlib import Path
UPLOAD_DIR = os.getenv('RAW_IMAGES_PATH','data/raw_images')
os.makedirs(UPLOAD_DIR, exist_ok=True)
def save_upload_files(files):
    saved=[]
    for f in files:
        ext = Path(f.filename).suffix
        name = f"{Path(f.filename).stem}_{uuid.uuid4().hex[:6]}{ext}"
        path = os.path.join(UPLOAD_DIR, name)
        f.save(path)
        saved.append({'path': path, 'name': name})
    return saved
