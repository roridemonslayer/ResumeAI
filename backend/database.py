from models import db

def init_db(app):
    """Initialize database with Flask app"""
    # Configure database settings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_ai.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from models import User, Resume, JobDecription, AnalysisResult
        db.create_all()
        print("Database tables created successfully!")
    
    return db