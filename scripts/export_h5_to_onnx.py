import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
    
import argparse
import tensorflow as tf
import tf2onnx

IMG_SIZE = 256

def convert(h5_path, onnx_path, opset=13):
    if not os.path.exists(h5_path):
        raise SystemExit(f"H5 model not found: {h5_path}")
    model = tf.keras.models.load_model(h5_path, compile=False)
    spec = (tf.TensorSpec((1, IMG_SIZE, IMG_SIZE, 3), tf.float32, name="input"),)
    print("Converting to ONNX (this may take a while)...")
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=opset)
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print("Saved ONNX ->", onnx_path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--h5", required=True)
    p.add_argument("--onnx", required=True)
    args = p.parse_args()
    os.makedirs(os.path.dirname(args.onnx) or ".", exist_ok=True)
    convert(args.h5, args.onnx)
