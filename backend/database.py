 #First, let's structure your database.py file:
#heres what to dom
#Import SQLAlchemy and create a database connection
#Define your models (User, Resume, JobDescription, AnalysisResult)
#Create relationships between models (User has many Resumes, etc.)

from flask import Flask, request, redirect, jsonify #requests handles incoming data and redorect jsut sends the user to another route or url
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
 user_id = db.Column(db.Integer, db.ForeginKey('users.id'))
 

    
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

