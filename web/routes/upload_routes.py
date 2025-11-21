from flask import Blueprint, request, jsonify
from ..services.file_service import save_upload_files
upload_bp = Blueprint('upload_bp', __name__)
@upload_bp.route('/', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error':'No files uploaded'}), 400
    saved = save_upload_files(files)
    return jsonify({'saved': saved})
