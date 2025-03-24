from flask import Blueprint, request, jsonify

analysis_blueprint = Blueprint('analysis', __name__)

@analysis_blueprint.route('/api/analysis/compare', methods=['POST'])
def analysis_compare():
    return jsonify({"message": "Comparison completed successfully"})