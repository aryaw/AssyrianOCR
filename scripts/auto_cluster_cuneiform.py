import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
    
import cv2
import numpy as np
from sklearn.cluster import KMeans
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.models import Model

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from scripts.cuneiform_pipeline_cpu import segment_and_extract_rois, resize_and_pad

base = MobileNetV2(weights="imagenet", include_top=False, pooling="avg")
embedder = Model(inputs=base.input, outputs=base.output)

IMG_SIZE = 96

def get_embedding(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    x = np.expand_dims(img, 0)
    x = preprocess_input(x)
    vec = embedder.predict(x, verbose=0)
    return vec[0]


def auto_cluster_tablet(img_bgr, k=6):
    rois = segment_and_extract_rois(img_bgr)

    if len(rois) == 0:
        return [], [], []

    embeddings = []
    for (x0, y0, x1, y1, roi) in rois:
        embeddings.append(get_embedding(roi))

    embeddings = np.array(embeddings)

    k = min(k, len(embeddings))

    kmeans = KMeans(n_clusters=k, random_state=42)
    cluster_ids = kmeans.fit_predict(embeddings)

    return rois, cluster_ids, embeddings


def export_clustered_dataset(rois, cluster_ids, out="data/cnn_auto/train"):
    os.makedirs(out, exist_ok=True)

    for i, ((x0, y0, x1, y1, roi_img), cid) in enumerate(zip(rois, cluster_ids)):
        cls_dir = os.path.join(out, f"cluster_{cid:03d}")
        os.makedirs(cls_dir, exist_ok=True)
        cv2.imwrite(os.path.join(cls_dir, f"roi_{i:04d}.png"), roi_img)

    return out
