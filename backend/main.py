from flask import Flask
from flask_cors import CORS
from database import init_db

# Import all blueprints
from auth_route import auth_blueprint
from resume_route import resume_blueprint
from job_route import job_blueprint
from profile_route import profile_blueprint
from analysis_route import analysis_blueprint

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure app settings
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'hfh38r83913103iqw920121123unsnuee'
    
    # Initialize database
    try:
        init_db(app)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return None
    
    # Enable CORS for frontend communication
    CORS(app)
    
    # Register all blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(resume_blueprint)
    app.register_blueprint(job_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(analysis_blueprint)
    
    print("All blueprints registered successfully!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    if app:
        print("Starting Flask application...")
        app.run(debug=True)
    else:
        print("Failed to create Flask application")