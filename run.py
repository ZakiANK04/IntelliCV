"""
AI CV Analyzer - Main Application Entry Point
Run this file to start the Flask development server.
"""
import os
from app import create_app, db
from app.models import AdminUser

# Create the Flask application
app = create_app()


def init_database():
    """Initialize database and create default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")


if __name__ == '__main__':
    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Run the application
    print("\n" + "="*60)
    print("  AI CV Analyzer - Starting Development Server")
    print("="*60)
    print(f"  * App URL: http://127.0.0.1:5000")
    print(f"  * Admin URL: http://127.0.0.1:5000/admin")
    print(f"  * Admin Login: username=admin, password=admin123")
    print("="*60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
