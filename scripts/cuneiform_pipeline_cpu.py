import os
import json
import cv2
import numpy as np
import onnxruntime as ort
from tensorflow.keras.models import load_model
from dotenv import load_dotenv

load_dotenv()

RAW_IMAGES_PATH = os.getenv("RAW_IMAGES_PATH")
DETECTOR_ONNX = os.getenv("DETECTOR_ONNX")
CLASSIFIER_H5 = os.getenv("CLASSIFIER_H5")
CLASS_INDICES = os.getenv("CLASS_INDICES")

IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", 256))
GRID_SIZE  = int(os.getenv("GRID_SIZE", 8))
ROI_SIZE   = int(os.getenv("ROI_SIZE", 64))

_classifier_model = None
_class_indices = None


def resize_and_pad(img, w, h, value=0):
    ih, iw = img.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)

    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((h, w), value, dtype=np.uint8)

    top = (h - nh) // 2
    left = (w - nw) // 2

    canvas[top:top+nh, left:left+nw] = resized
    return canvas


def preprocess_tablet(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thr = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        15, 5
    )
    return thr


def segment_and_extract_rois(img_bgr, min_area=50, max_area=50000):
    prep = preprocess_tablet(img_bgr)
    contours, _ = cv2.findContours(prep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rois = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w*h < min_area or w*h > max_area:
            continue

        roi = img_bgr[y:y+h, x:x+w]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_norm = resize_and_pad(roi_gray, ROI_SIZE, ROI_SIZE)

        rois.append((x, y, x+w, y+h, roi_norm))

    return rois


def load_onnx_detector():
    if not os.path.exists(DETECTOR_ONNX):
        return None
    return ort.InferenceSession(DETECTOR_ONNX)


def infer_onnx_boxes(img_bgr, sess, conf_th=0.25):
    H, W = img_bgr.shape[:2]
    resized = cv2.resize(img_bgr, (IMAGE_SIZE, IMAGE_SIZE))
    blob = resized.astype(np.float32)/255.0
    blob = blob.transpose(2,0,1)
    blob = np.expand_dims(blob, 0)

    inp = sess.get_inputs()[0].name
    out = sess.get_outputs()[0].name

    pred = sess.run([out], {inp: blob})[0][0]

    boxes = []
    cell_w = W / GRID_SIZE
    cell_h = H / GRID_SIZE

    for iy in range(GRID_SIZE):
        for ix in range(GRID_SIZE):
            x, y, w, h, obj = pred[iy, ix]
            if obj < conf_th:
                continue

            cx = (ix + x) * cell_w
            cy = (iy + y) * cell_h
            bw = w * W
            bh = h * H

            x0 = int(cx - bw/2)
            y0 = int(cy - bh/2)
            x1 = int(cx + bw/2)
            y1 = int(cy + bh/2)

            boxes.append([x0,y0,x1,y1,float(obj)])

    return boxes


def contour_detector(prep_img):
    cnts, _ = cv2.findContours(prep_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w*h > 50:
            out.append([x,y,x+w,y+h,1.0])
    return out


def extract_rois(img_bgr, boxes):
    rois = []
    pos  = []

    for (x0,y0,x1,y1,conf) in boxes:
        x0 = max(0,x0)
        y0 = max(0,y0)
        roi = img_bgr[y0:y1, x0:x1]

        if roi.size == 0:
            continue

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        rs   = cv2.resize(gray, (ROI_SIZE, ROI_SIZE))

        rs = rs.astype("float32")/255.0
        rs = np.expand_dims(rs, -1)

        rois.append(rs)
        pos.append((x0,y0,x1,y1,conf))

    if not rois:
        return None, None

    return np.array(rois), pos


def load_classifier():
    global _classifier_model, _class_indices

    if _classifier_model is None:
        _classifier_model = load_model(CLASSIFIER_H5)

    if _class_indices is None:
        with open(CLASS_INDICES) as f:
            _class_indices = json.load(f)

    return _classifier_model, _class_indices


def classify_rois(rois):
    model, idx = load_classifier()
    preds = model.predict(rois, verbose=0)
    inv = {v:k for k,v in idx.items()}

    out = []
    for p in preds:
        cid  = int(np.argmax(p))
        conf = float(np.max(p))
        out.append((inv.get(cid,"?"), conf))

    return out


def transliterate_sequence(labels):
    mapping = {
        "AN": "an",
        "DINGIR": "dingir",
        "NI": "ni",
        "GI": "gi",
        "A": "a",
        "U": "u"
    }
    return " ".join(mapping.get(lbl,lbl) for lbl in labels)


def process_tablet_image(img_bgr):
    prep = preprocess_tablet(img_bgr)

    sess = load_onnx_detector()
    if sess:
        boxes = infer_onnx_boxes(img_bgr, sess)
    else:
        boxes = contour_detector(prep)

    rois, pos = extract_rois(img_bgr, boxes)
    if rois is None:
        return [], [], ""

    cls = classify_rois(rois)
    labels = [c[0] for c in cls]

    translit = transliterate_sequence(labels)

    return pos, cls, translit
