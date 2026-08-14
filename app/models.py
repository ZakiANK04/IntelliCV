"""
Database Models for AI CV Analyzer
"""
from datetime import datetime
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db, login_manager


class User(db.Model):
    """User model for CV submissions"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    cv_analyses: Mapped[list["CVAnalysis"]] = relationship(
        "CVAnalysis", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.id}: {self.full_name}>"
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CVAnalysis(db.Model):
    """CV Analysis results model"""
    __tablename__ = 'cv_analysis'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    # File info
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Extracted content
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    text_length: Mapped[int] = mapped_column(Integer, default=0)
    
    # Overall results
    score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_level: Mapped[str] = mapped_column(String(50), nullable=True)
    career_field: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Detailed analysis (stored as JSON)
    analysis_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Score breakdown
    experience_score: Mapped[float] = mapped_column(Float, default=0.0)
    skills_score: Mapped[float] = mapped_column(Float, default=0.0)
    structure_score: Mapped[float] = mapped_column(Float, default=0.0)
    career_score: Mapped[float] = mapped_column(Float, default=0.0)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Detected sections
    sections_detected: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Skills found
    skills_found: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Recommendations
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time: Mapped[float] = mapped_column(Float, default=0.0)  # in seconds
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="cv_analyses")
    
    def __repr__(self) -> str:
        return f"<CVAnalysis {self.id}: Score {self.score}>"
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'original_filename': self.original_filename,
            'score': self.score,
            'experience_level': self.experience_level,
            'career_field': self.career_field,
            'analysis_json': self.analysis_json,
            'experience_score': self.experience_score,
            'skills_score': self.skills_score,
            'structure_score': self.structure_score,
            'career_score': self.career_score,
            'readability_score': self.readability_score,
            'sections_detected': self.sections_detected,
            'skills_found': self.skills_found,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processing_time': self.processing_time
        }


class AdminUser(db.Model, UserMixin):
    """Admin user for dashboard access"""
    __tablename__ = 'admin_users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        return f"<AdminUser {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return AdminUser.query.get(int(user_id))
