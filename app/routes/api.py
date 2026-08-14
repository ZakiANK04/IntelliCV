"""
API routes for the AI CV Analyzer
Handles AJAX requests for CV processing
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app import db, csrf
from app.models import User, CVAnalysis
from app.services.cv_analyzer import cv_analyzer_service

api_bp = Blueprint('api', __name__)

# Exempt API routes from CSRF protection (they use JSON/FormData)
csrf.exempt(api_bp)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@api_bp.route('/submit-user', methods=['POST'])
def submit_user():
    """
    Submit user information before CV upload.
    Creates user record and returns user_id.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create user record
        user = User(
            full_name=data['full_name'].strip(),
            email=data['email'].strip().lower(),
            phone=data['phone'].strip()
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'message': 'User information saved successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/upload-cv', methods=['POST'])
def upload_cv():
    """
    Upload and analyze CV file.
    Requires user_id from previous step.
    """
    try:
        # Get user_id
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check for file
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['cv_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure the filename
        original_filename = secure_filename(file.filename)
        
        # Process the CV
        success, message, analysis = cv_analyzer_service.process_cv(
            user_id=int(user_id),
            pdf_file=file,
            original_filename=original_filename
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'success': True,
            'analysis_id': analysis.id,
            'message': message,
            'redirect_url': f'/results/{analysis.id}'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get analysis results by ID"""
    analysis = CVAnalysis.query.get_or_404(analysis_id)
    return jsonify(analysis.to_dict())


@api_bp.route('/analysis/<int:analysis_id>/summary', methods=['GET'])
def get_analysis_summary(analysis_id):
    """Get summary of analysis for quick display"""
    analysis = CVAnalysis.query.get_or_404(analysis_id)
    
    return jsonify({
        'id': analysis.id,
        'score': analysis.score,
        'experience_level': analysis.experience_level,
        'career_field': analysis.career_field,
        'skills_count': len(analysis.skills_found) if analysis.skills_found else 0,
        'sections_detected': sum(
            1 for s in (analysis.sections_detected or {}).values()
            if s.get('detected')
        ),
        'processing_time': analysis.processing_time
    })


@api_bp.route('/validate-pdf', methods=['POST'])
def validate_pdf():
    """Validate PDF file before full upload"""
    if 'file' not in request.files:
        return jsonify({'valid': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'valid': False, 'error': 'Only PDF files are allowed'}), 400
    
    # Check file header
    header = file.read(8)
    file.seek(0)  # Reset file pointer
    
    if not header.startswith(b'%PDF'):
        return jsonify({'valid': False, 'error': 'Invalid PDF format'}), 400
    
    return jsonify({
        'valid': True,
        'filename': secure_filename(file.filename)
    })


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    total_users = User.query.count()
    total_analyses = CVAnalysis.query.count()
    
    avg_score = db.session.query(db.func.avg(CVAnalysis.score)).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'total_analyses': total_analyses,
        'average_score': round(float(avg_score), 2)
    })
