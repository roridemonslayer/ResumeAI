from flask import Flask  # importing the flask module
from flask_cors import CORS  # initializing the cors module
# cors allows the frontend to communicate with the backend. like a hall pass
from database import init_db

from auth_route import auth_blueprint
from resume_route import resume_blueprint
from job_route import job_blueprint
from profile_route import profile_blueprint
from analysis_route import analysis_blueprint

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True  # this allows the app to run in debug mode and show error
    app.config['SECRET_KEY'] = 'hfh38r83913103iqw920121123unsnuee'
    #this js initizalizes the database
    init_db(app)
    #cors enables frontend backend connectio
    CORS(app)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(resume_blueprint)
    app.register_blueprint(job_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(analysis_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug = True)