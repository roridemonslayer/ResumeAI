from flask import Blueprint, request, jsonify

profile_blueprint = Blueprint('profile', __name__)

@profile_blueprint.route('/api/profile/resume', methods=['POST'])
def create_profile():
    return jsonify({'message': 'Resume Fetched successfully'})

@profile_blueprint.route('/api/profile/history', methods = ['GET'])
def get_history():
    return jsonify({'message': 'History retrieved successfully'})

@profile_blueprint.route('/api/profile/stats', methods = ['GET'])
def get_stats():
    return jsonify({'message': 'Stats retrieved successfully'})