from flask import Blueprint, request, jsonify

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/api/auth/signup', methods=['POST'])
def signUp():
    return jsonify({"message": "Signup successful"})

@auth_blueprint.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({"message": "Login successful"})
