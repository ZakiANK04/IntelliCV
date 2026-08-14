"""
Main routes for the AI CV Analyzer
Handles frontend page rendering
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@main_bp.route('/upload')
def upload():
    """CV upload page"""
    return render_template('upload.html')


@main_bp.route('/results/<int:analysis_id>')
def results(analysis_id):
    """Results page for a specific analysis"""
    from app.models import CVAnalysis
    
    analysis = CVAnalysis.query.get_or_404(analysis_id)
    return render_template('results.html', analysis=analysis)


@main_bp.route('/documentation')
def documentation():
    """Project documentation page"""
    return render_template('documentation.html')


@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files (for admin use)"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
