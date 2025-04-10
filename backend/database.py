 #First, let's structure your database.py file:
#heres what to dom
#Import SQLAlchemy and create a database connection
#Define your models (User, Resume, JobDescription, AnalysisResult)
#Create relationships between models (User has many Resumes, etc.)

from flask import Flask
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_ai.db' # just tell sqlalchemy where ur db is 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #this just prevents unccary tracking in ur sql

db = SQLAlchemy(app) #sql instance

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True) #the primary key is just so that two rows dont have the same primary key
    #only one or more table can have one primary key
    fullName = db.Column(db.String(200), nullable = False) #nullable just menasts it cant be empty
    email = db.Column(db.String(200), nullable  = False) 
    password = db.Columb(db.String(50), nullable = False)



 

class Resume(db.Model):
 __tablename__ = "resume"
 id = db.Column(db.Integer, primary_key = True)
 user_id = db.Column(db.Integer, db.ForeginKey('users.id'), nullable = False)
 title = db.Column(db.String(200), nullable = False) #this is for the title of the resume
 file_path = db.Column(db.Text)  #the reason we have a file_path column is cuz some users are gonna add their pdf, DOCXA OR LIKE OHTER file format so this is where u can store the location of the file in serve or cloud storage
 content = db.Column(db.Text, nullable = False) #the use of db.Text, just allows you to store large amounts of text without any cap value
 parsed_data = db.Column(db.Text) #this is useful when converting the raw data into structed JSON data
 created_at = db.Column(db.DateTime, default = datetime.utcnow) # this just allows the datetime sto be shown regardless of wehre u are in the world. its univseralal time 
 updated_at = db.Column(db.DateTime, defualt = datetime.utcnow)


    
class AnalysisResult(db.Model):
  __tablename__ = "analysis"
  id  = db.Column( db.Integer, primary_key = True)

 
class JobDecription(db.Model):
 _tablename = "description"
 id = db.Column(db.Integer, primary_key = True)
 



 if __name__ == "__name__":
    with app.app_context():  #needed for db operation
      db.create_all() #creates the db and tables
    #allwayes goes at the end 

