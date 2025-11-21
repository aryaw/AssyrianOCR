from flask import Blueprint, request, jsonify
from ..services.cnn_training_service import train_from_cluster_dir
training_bp = Blueprint('training_bp', __name__)
@training_bp.route('/cnn', methods=['POST'])
def train_cnn():
    data = request.get_json() or {}
    epochs = int(data.get('epochs', 10))
    res = train_from_cluster_dir(epochs=epochs)
    return jsonify(res)
