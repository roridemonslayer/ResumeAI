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
    password = db.Column(db.String(50), nullable = False)



 

class Resume(db.Model):
  __tablename__ = "resume"
  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
  title = db.Column(db.String(200), nullable = False) #this is for the title of the resume
  file_path = db.Column(db.Text)  #the reason we have a file_path column is cuz some users are gonna add their pdf, DOCXA OR LIKE OHTER file format so this is where u can store the location of the file in serve or cloud storagecontent = db.Column(db.Text, nullable = False) #the use of db.Text, just allows you to store large amounts of text without any cap value
  parsed_data = db.Column(db.Text) #this is useful when converting the raw data into structed JSON data
  created_at = db.Column(db.DateTime, default = datetime.utcnow) # this just allows the datetime sto be shown regardless of wehre u are in the world. its univseralal time 
  updated_at = db.Column(db.DateTime, default = datetime.utcnow, onupdate = datetime.utcnow) #thifs just records the time the resume everytime its updated 
#helper methods so these helper methods basically small functions inside ur code and u can call method when u need something reused to write somethign for u 
#were going use this method to convert our parsed data into JSON data. 
#1st
  def get_parsed_data(self):  #self is just used to refer to the fact that this instance is particular to resume 
    if self.parsed_data: # what this does is like, if theres anythign in our parsed_data, just check
      return json.loads(self.parsed_data)# what json loads does, is basically just decodes a josn string into a python dictionary 
    return{} #it returns nothing if theres no parsed data found
#2nd
  def set_parsed_data(self, data_dict): #what data_dict is, is just like what u wanna save basically 
    self.parsed_data = json.dumps(data_dict)#were using this because when u have a python dict, u cant jsut save it directly
    # so to simplify everything, set just sets the databse somewhere for the computer and converts it into strings 
    #get just gets it for later when u need it again and need to work with it
class AnalysisResult(db.Model):
  __tablename__ = "analysis"
  id  = db.Column( db.Integer, primary_key = True)
  

 
class JobDecription(db.Model):
  _tablename = "description"
  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  title = db.Column(db.String(300), nullable = False) 
  company = db.Column(db.String(100), nullable = False)
  content = db.Column(db.Text)
  keywords = db.Column(db.Text)
  created_at  = db.Column(db.DateTime, default = datetime.utcnow)
  user = db.relationship('User', backref ='description' )

  def get_keywords(self):
    if self.keywords:
      return json.loads(self.keywords)
    return[]
  def set_keywords(self, keywords_list):
    self.keywords = json.dumps(keywords_list)

class AnalysisResult(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  resume_id = db.Column(db.Integet, db.ForeignKey("resume.id"), nullable = False)
  job_id = db.Column(db.Integet, db.ForeignKey("description.id"), nullable = False)
  match_percentage = db.Column(db.Float)  #this generates the match percentage of each persons resume
  keywords_match= db.Column(db.Float) #this calculates what precentage the words match to the description 
  skills_allignment = db.Column(db.String(50)) # generates through text how strong or weak the  skills are 
  format_compatibality = db.Column(db.String(50)) #generates how close to format the resume is 
  improvements = db.Column(db.Text) #which just shows like, what improvements users need to make to their resume
  created_at = db.Column(db.DateTime, defualt = datetime.utcnow)

  user= db.relationship("User", backref = "analysis")
  resume = db.relationship("Resume", backref = "analysis")
  job = db.relationship("JobDescription", backref = "analysis")

  def get_analysis(self):
    if self.analysis:
      return json.loads(self.analysis)
    return[]

  def set_analysis(self, anaylsis_list):
    self.analysis = json.dumps(anaylsis_list)

if __name__ == "__name__":
    with app.app_context():  #needed for db operation
      db.create_all() #creates the db and tables
    #allwayes goes at the end 

