# Assyrian Script OCR

A Flask-based application for image clustering, annotation, and data export.  
Supports multi-image upload, K-means clustering, annotated previews, cropped ROIs, CSV/JSON exports, and model interactions.

---

## Features

### ✔ Upload Multiple Images
Users can upload multiple assyrian script images at once.

### ✔ Automated Clustering
Each image is processed using:
- Feature extraction
- Auto-clustering (K-Means or custom algorithm)
- Bounding box identification

### ✔ Annotated Output Images
The system saves:
- `clustered_{timestamp}.png`  
With bounding boxes and cluster labels.

### ✔ CSV & JSON Export
Each image generates:
- `cluster_result_{timestamp}.csv`
- `cluster_result_{timestamp}.json`

### ✔ Cropped ROI Export
Each bounding box is cropped and saved:
- Grouped by image
- Named by cluster and box index

### ✔ REST API Endpoints
| Endpoint | Method | Description |
|---------|--------|-------------|
| `/api/upload/` | POST | Upload multiple images |
| `/api/cluster/run` | POST | Run clustering on one or more images |
| `/api/models/...` | GET/POST | Model operations |
| `/api/health/` | GET | Health check |

---

## 📂 Project Structure
```
project/
│
├── web/
│   ├── routes/
│   ├── templates/
│   └── static/
│
├── data/
│   ├── raw_images/    <-uploaded images
│   └── output/
│       ├── csv/
│       ├── json/
│       ├── img_clustered/
│       └── crops/
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Installation

### 1. Clone the repository
```
git clone https://github.com/this/repo.git
cd this-repo
```

### 2. Create virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

---

## Running the App
```
python app.py
```

Server will start at:

```
http://localhost:8501
```

---

## API Example Request

### POST `/api/cluster/run`

```json
{
  "images": [
    "data/raw_images/1.jpg",
    "data/raw_images/2.jpg"
  ],
  "k": 8
}
```

### Response

```json
{
  "results": [
    {
      "image": "data/raw_images/1.jpg",
      "csv": "data/output/csv/1_cluster_2025-11-16_12-00-00.csv",
      "json": "data/output/json/1_cluster_2025-11-16_12-00-00.json",
      "clustered_image": "data/output/img_clustered/1_clustered_2025-11-16_12-00-00.png",
      "crops": [
        "data/output/crops/1/1_cluster_0_box_0.png",
        "data/output/crops/1/1_cluster_1_box_1.png"
      ],
      "timestamp": "2025-11-16_12-00-00"
    }
  ]
}
```


---

## Next Development Phase (Planned Updates)

The following features are planned for the upcoming version of Assyrian Script OCR.
These upgrades will extend the system from pure clustering + restoration into a complete OCR + Transliteration + Translation pipeline.

### Phase 1 - Latin Transliteration (Assyrian → Latin)

A new module will be added to convert clustered/cropped cuneiform symbols into Latin-character transliterations


### Target Dataset

Cuneiform Sign Images Dataset (Kaggle)
This dataset will be used to train the first version of the Latin transliteration model.

Dataset:
https://www.kaggle.com/datasets/paultimothymooney/cuneiform-sign-images

### Phase 2 - Machine Translation (English → Bahasa Indonesia)

Integrate a translation pipeline allowing OCR’d English text to be translated to Indonesian.
(This is optional and will be an extra button in the UI.)

### Phase 3 - Unified Full Pipeline (End-to-End)

Future Combined Flow:
- Upload Image
- Preprocessing + Restoration
- Segmentation + Clustering
- OCR (Latin characters)
- Transliteration (Assyrian → Latin)
- Translation (EN → ID)

---
## License
This project is licensed under the MIT License.