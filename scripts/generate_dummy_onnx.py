import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
    
import tensorflow as tf
import tf2onnx

from tensorflow.keras import layers, models

IMG_SIZE = 256
GRID = 8
NUM_BOX_PARAMS = 5
OUT_ONNX = "models/detector_yoloV2.onnx"

os.makedirs(os.path.dirname(OUT_ONNX), exist_ok=True)

def build_detector():
    base = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights=None
    )
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(base.output)
    x = layers.Conv2D(NUM_BOX_PARAMS, 1, padding="same")(x)
    out = layers.Reshape((GRID, GRID, NUM_BOX_PARAMS))(x)
    model = models.Model(inputs=base.input, outputs=out)
    return model

def export_onnx_from_keras(model, out_path):
    spec = (tf.TensorSpec((1, IMG_SIZE, IMG_SIZE, 3), tf.float32, name="input"),)
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)
    with open(out_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

if __name__ == "__main__":
    print("Building dummy detector model (random weights)...")
    m = build_detector()
    print("Exporting to ONNX:", OUT_ONNX)
    export_onnx_from_keras(m, OUT_ONNX)
    print("Done. Dummy ONNX saved to", OUT_ONNX)
