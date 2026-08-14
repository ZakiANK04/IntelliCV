"""
Configuration settings for AI CV Analyzer
"""
import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ai-cv-analyzer-secret-key-2024'
    
    # Database - SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Allow overriding database path for Docker volumes (e.g., /app/data/app.db)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite specific engine options
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # File Upload
    # Allow overriding upload folder for Docker volumes (e.g., /app/data/uploads)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Admin credentials (for school project)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # NLP Settings
    SPACY_MODEL = 'en_core_web_sm'
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        'experience_level': 25,
        'skills_relevance': 25,
        'cv_structure': 20,
        'career_alignment': 15,
        'readability': 15
    }
    
    # CV Sections to detect
    CV_SECTIONS = [
        'professional_summary',
        'education',
        'work_experience',
        'internship_experience',
        'skills',
        'projects',
        'certifications',
        'achievements',
        'hobbies'
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
