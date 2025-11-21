from flask import Blueprint, send_file, abort
import os
model_bp = Blueprint('model_bp', __name__)
@model_bp.route('/<path:fname>')
def download_model(fname):
    path = os.path.join('models', fname)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    abort(404)
