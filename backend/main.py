from flask import Flask  # importing the flask module
from flask_cors import CORS  # initializing the cors module
# cors allows the frontend to communicate with the backend. like a hall pass
from database import db

from auth_route import auth_blueprint
from resume_route import resume_blueprint
from job_route import job_blueprint
from profile_route import profile_blueprint
from analysis_route import analysis_blueprint

app = Flask(__name__)  # this is just the configuration of the app
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///resume_ai.db' 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG'] = True  # this allows the app to run in debug mode and show errors
app.config['SECRET_KEY'] = 'hfh38r83913103iqw920121123unsnuee'
db.init_app(app)
CORS(app)


app.register_blueprint(auth_blueprint)
app.register_blueprint(resume_blueprint)
app.register_blueprint(job_blueprint)
app.register_blueprint(profile_blueprint)
app.register_blueprint(analysis_blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
