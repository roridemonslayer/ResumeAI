 #First, let's structure your database.py file:
#heres what to dom
#Import SQLAlchemy and create a database connection
#Define your models (User, Resume, JobDescription, AnalysisResult)
#Create relationships between models (User has many Resumes, etc.)

from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_URI'] = 'sqlite:///resume_ai.db' # just tell sqlalchemy where ur db is 
app.config['SQLALTHEMY_TRACK_MODIFICATIONS'] = False #this just prevents unccary tracking in ur sql

class User(db.Model):
    id =
    fullName = 
    email = 
    password = 



 

class Resume(db.Model):

    
class AnalysisResult(db.Model):
