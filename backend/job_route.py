from flask import Blueprint, request, jsonify

job_blueprint = Blueprint('job', __name__)

@job_blueprint.route("/api/job/submitDes", methods = ['POST'])
def submit_description():
    return jsonify({'message': 'Job description submitted successfully'})

@job_blueprint.route("/api/job/saveDes", methods = ['POST'])
def save_description():
    return jsonify({'message': 'Job description saved successfully'})