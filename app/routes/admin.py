"""
Admin routes for the AI CV Analyzer
Handles admin dashboard, authentication, and data export
"""
import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import AdminUser, User, CVAnalysis

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check hardcoded credentials first
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            
            # Get or create admin user
            admin = AdminUser.query.filter_by(username=username).first()
            if not admin:
                admin = AdminUser(username=username)
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
            
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(admin)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        # Check database credentials
        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(admin)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_analyses = CVAnalysis.query.count()
    avg_score = db.session.query(db.func.avg(CVAnalysis.score)).scalar() or 0
    
    # Get recent analyses
    recent_analyses = CVAnalysis.query.order_by(
        CVAnalysis.created_at.desc()
    ).limit(10).all()
    
    # Get score distribution
    score_ranges = {
        '0-20': CVAnalysis.query.filter(CVAnalysis.score < 20).count(),
        '20-40': CVAnalysis.query.filter(CVAnalysis.score >= 20, CVAnalysis.score < 40).count(),
        '40-60': CVAnalysis.query.filter(CVAnalysis.score >= 40, CVAnalysis.score < 60).count(),
        '60-80': CVAnalysis.query.filter(CVAnalysis.score >= 60, CVAnalysis.score < 80).count(),
        '80-100': CVAnalysis.query.filter(CVAnalysis.score >= 80).count()
    }
    
    # Get experience level distribution
    exp_distribution = db.session.query(
        CVAnalysis.experience_level,
        db.func.count(CVAnalysis.id)
    ).group_by(CVAnalysis.experience_level).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_analyses=total_analyses,
                          avg_score=round(float(avg_score), 2),
                          recent_analyses=recent_analyses,
                          score_ranges=score_ranges,
                          exp_distribution=dict(exp_distribution))


@admin_bp.route('/submissions')
@login_required
def submissions():
    """List all CV submissions"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Search and filter
    search = request.args.get('search', '')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)
    experience = request.args.get('experience', '')
    
    query = CVAnalysis.query.join(User)
    
    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                CVAnalysis.career_field.ilike(f'%{search}%')
            )
        )
    
    if min_score is not None:
        query = query.filter(CVAnalysis.score >= min_score)
    
    if max_score is not None:
        query = query.filter(CVAnalysis.score <= max_score)
    
    if experience:
        query = query.filter(CVAnalysis.experience_level == experience)
    
    submissions = query.order_by(CVAnalysis.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/submissions.html',
                          submissions=submissions,
                          search=search,
                          min_score=min_score,
                          max_score=max_score,
                          experience=experience)


@admin_bp.route('/submission/<int:analysis_id>')
@login_required
def view_submission(analysis_id):
    """View detailed submission"""
    analysis = CVAnalysis.query.get_or_404(analysis_id)
    return render_template('admin/view_submission.html', analysis=analysis)


@admin_bp.route('/submission/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete_submission(analysis_id):
    """Delete a submission"""
    from app.services.cv_analyzer import cv_analyzer_service
    
    if cv_analyzer_service.delete_analysis(analysis_id):
        flash('Submission deleted successfully!', 'success')
    else:
        flash('Failed to delete submission', 'error')
    
    return redirect(url_for('admin.submissions'))


@admin_bp.route('/export/csv')
@login_required
def export_csv():
    """Export all submissions to CSV"""
    analyses = CVAnalysis.query.join(User).order_by(CVAnalysis.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Full Name', 'Email', 'Phone',
        'Score', 'Experience Level', 'Career Field',
        'Experience Score', 'Skills Score', 'Structure Score',
        'Career Score', 'Readability Score',
        'Skills Found', 'Submitted At', 'Processing Time'
    ])
    
    # Write data
    for analysis in analyses:
        writer.writerow([
            analysis.id,
            analysis.user.full_name,
            analysis.user.email,
            analysis.user.phone,
            analysis.score,
            analysis.experience_level,
            analysis.career_field,
            analysis.experience_score,
            analysis.skills_score,
            analysis.structure_score,
            analysis.career_score,
            analysis.readability_score,
            ', '.join(analysis.skills_found or []),
            analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            f"{analysis.processing_time}s"
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=cv_submissions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )


@admin_bp.route('/users')
@login_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)
