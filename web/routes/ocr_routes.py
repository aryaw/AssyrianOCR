from flask import Blueprint, request, jsonify
import pytesseract
from PIL import Image
import os
from argostranslate import package, translate

ocr_bp = Blueprint("ocr_bp", __name__)

ENV_DEFAULT_LANG = os.getenv("ENV_TRANSLATE", "id")

TRANSLATORS = {}

def ensure_translation_model(from_code="en", to_code="id"):
    installed = package.get_installed_packages()

    for p in installed:
        if p.from_code == from_code and p.to_code == to_code:
            translate.load_installed_languages()
            return translate.Translator.from_codes(from_code, to_code)

    available = package.get_available_packages()
    for p in available:
        if p.from_code == from_code and p.to_code == to_code:
            pkg = p.download()
            package.install_from_path(pkg)
            translate.load_installed_languages()
            return translate.Translator.from_codes(from_code, to_code)

    return None


def get_translator(to_code):
    if to_code in TRANSLATORS:
        return TRANSLATORS[to_code]

    tr = ensure_translation_model("en", to_code)
    if tr:
        TRANSLATORS[to_code] = tr
    return tr


@ocr_bp.route("/run", methods=["POST"])
def run_ocr():
    data = request.get_json() or {}

    crop_paths = data.get("crops", [])
    translate_to = data.get("to") or ENV_DEFAULT_LANG

    if not crop_paths:
        return jsonify({"error": "no crops provided"}), 400

    translator = get_translator(translate_to)
    if translator is None:
        return jsonify({
            "error": f"Translation model EN → {translate_to} missing and not available."
        }), 400

    results = []
    ocr_output = []

    out_dir = "data/output/ocr"
    os.makedirs(out_dir, exist_ok=True)

    for rel_path in crop_paths:
        full_path = os.path.join(os.getcwd(), rel_path)

        try:
            img = Image.open(full_path)
            text = pytesseract.image_to_string(img, lang="eng").strip()
            translated = translator.translate(text).strip()

            item = {
                "image": rel_path,
                "ocr": text,
                "translated": translated
            }

            ocr_output.append(item)
            results.append(item)

        except Exception as e:
            results.append({
                "image": rel_path,
                "error": str(e)
            })

    import csv, json
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_path = os.path.join(out_dir, f"ocr_translate_{ts}.csv")
    json_path = os.path.join(out_dir, f"ocr_translate_{ts}.json")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "ocr", "translated"])
        for r in ocr_output:
            writer.writerow([
                r["image"],
                r["ocr"].replace("\n", " "),
                r["translated"].replace("\n", " ")
            ])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ocr_output, f, indent=2)

    return jsonify({
        "results": results,
        "csv": csv_path,
        "json": json_path
    })
