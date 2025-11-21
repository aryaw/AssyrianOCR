import pytesseract
from PIL import Image
from argostranslate import package, translate
import os

def load_model(from_code="en", to_code="id"):
    available_packages = package.get_available_packages()
    for p in available_packages:
        if p.from_code == from_code and p.to_code == to_code:
            package.install_from_path(p.download())
            break

    translate.load_installed_packages()

load_model("en", "id")

def ocr_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"[OCR ERROR] {e}"

def translate_text(text, from_lang="en", to_lang="id"):
    try:
        translated = translate.translate(text, from_lang, to_lang)
        return translated
    except Exception as e:
        return f"[TRANSLATE ERROR] {e}"

def ocr_and_translate(image_path, from_lang="en", to_lang="id"):
    text = ocr_image(image_path)
    translated = translate_text(text, from_lang, to_lang)
    return {
        "ocr_text": text,
        "translated_text": translated
    }
