from  flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from models import db 

def init(app):
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_ai.db'
  app.config["SQLALCEHMY_TRACK_MODIFICATIONS"] = False #this basically like means it wont track uncceaarty things

  db.init_app(app)

  with app.app_context():
    db.create_all()
  return db
