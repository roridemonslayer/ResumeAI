from flask import Blueprint, request, jsonify
resume_blueprint = Blueprint('resume', __name__)

@resume_blueprint.route('/api/resume/download', methods=['POST'])
def resume_download():
    return jsonify({'message': 'Resume downloaded successfully'})

@resume_blueprint.route("/api/resume/upload", methods = ['POST'])
def resume_upload():
    return jsonify({'message': 'Resume uploaded successfully'})

@resume_blueprint.route("/api/resume/list", methods = ['GET'])
def resume_list():
    return jsonify({'message': 'Resume list retrieved successfully'})

@resume_blueprint.route('/api/resume/edit', methods = ['PUT'])
def resume_edit():
    return jsonify({'message': 'Resume edited successfully'})

@resume_blueprint.route('/api/resume/version', methods = ['POST'])
def resume_version():
    return jsonify({'message': 'Resume version created successfulleyg'})