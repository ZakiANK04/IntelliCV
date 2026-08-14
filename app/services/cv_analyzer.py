"""
CV Analysis Orchestrator
Coordinates PDF extraction, NLP analysis, and result generation
"""
import os
import time
import uuid
import logging
from typing import Tuple, Optional
from dataclasses import asdict

from werkzeug.utils import secure_filename
from flask import current_app

from app import db
from app.models import User, CVAnalysis
from app.services.pdf_extractor import pdf_extractor
from app.services.nlp_analyzer import nlp_analyzer, AnalysisResult

logger = logging.getLogger(__name__)


class CVAnalyzerService:
    """
    Main service for CV analysis workflow.
    Orchestrates PDF extraction, NLP processing, and database storage.
    """
    
    def __init__(self):
        pass
    
    def process_cv(
        self,
        user_id: int,
        pdf_file,
        original_filename: str
    ) -> Tuple[bool, str, Optional[CVAnalysis]]:
        """
        Process uploaded CV file.
        
        Args:
            user_id: ID of the user who submitted the CV
            pdf_file: File object from request
            original_filename: Original filename
            
        Returns:
            Tuple of (success, message, cv_analysis_object)
        """
        start_time = time.time()
        
        # Generate unique filename
        file_ext = os.path.splitext(original_filename)[1]
        stored_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
        
        try:
            # Save the uploaded file
            pdf_file.save(file_path)
            logger.info(f"Saved uploaded file: {stored_filename}")
            
            # Validate PDF
            is_valid, error_msg = pdf_extractor.validate_pdf(file_path)
            if not is_valid:
                os.remove(file_path)
                return False, f"Invalid PDF: {error_msg}", None
            
            # Extract text
            extracted_text, extraction_metadata = pdf_extractor.extract_text(file_path)
            
            if not extraction_metadata['success']:
                os.remove(file_path)
                return False, "Failed to extract text from PDF", None
            
            logger.info(f"Extracted {len(extracted_text)} characters using {extraction_metadata['method']}")
            
            # Perform NLP analysis
            analysis_result = nlp_analyzer.analyze(extracted_text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create CV analysis record
            cv_analysis = CVAnalysis(
                user_id=user_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                extracted_text=extracted_text,
                text_length=len(extracted_text),
                score=round(analysis_result.overall_score, 2),
                experience_level=analysis_result.experience_level,
                career_field=analysis_result.career_field,
                experience_score=round(analysis_result.experience_score, 2),
                skills_score=round(analysis_result.skills_score, 2),
                structure_score=round(analysis_result.structure_score, 2),
                career_score=round(analysis_result.career_score, 2),
                readability_score=round(analysis_result.readability_score, 2),
                sections_detected=self._sections_to_dict(analysis_result.sections),
                skills_found=analysis_result.skills_found,
                recommendations={
                    'strengths': analysis_result.strengths,
                    'weaknesses': analysis_result.weaknesses,
                    'recommendations': analysis_result.recommendations,
                    'youtube_suggestions': analysis_result.youtube_suggestions
                },
                analysis_json={
                    'entities': analysis_result.entities,
                    'extraction_method': extraction_metadata['method'],
                    'pages_processed': extraction_metadata['pages'],
                    'extraction_warnings': extraction_metadata['warnings']
                },
                processing_time=round(processing_time, 2)
            )
            
            # Save to database
            db.session.add(cv_analysis)
            db.session.commit()
            
            logger.info(f"CV analysis completed. Score: {cv_analysis.score}, Time: {processing_time:.2f}s")
            
            return True, "CV analyzed successfully", cv_analysis
            
        except Exception as e:
            logger.error(f"CV processing failed: {e}")
            db.session.rollback()
            
            # Clean up file if it was saved
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            return False, f"Processing error: {str(e)}", None
    
    def _sections_to_dict(self, sections: dict) -> dict:
        """Convert sections to JSON-serializable format"""
        result = {}
        for name, section in sections.items():
            result[name] = {
                'detected': section.detected,
                'quality_score': round(section.quality_score, 2),
                'explanation': section.explanation
            }
        return result
    
    def get_analysis(self, analysis_id: int) -> Optional[CVAnalysis]:
        """Get CV analysis by ID"""
        return CVAnalysis.query.get(analysis_id)
    
    def get_user_analyses(self, user_id: int) -> list:
        """Get all analyses for a user"""
        return CVAnalysis.query.filter_by(user_id=user_id).order_by(
            CVAnalysis.created_at.desc()
        ).all()
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete CV analysis and associated file"""
        try:
            analysis = CVAnalysis.query.get(analysis_id)
            if not analysis:
                return False
            
            # Delete file
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                analysis.stored_filename
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete database record
            db.session.delete(analysis)
            db.session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete analysis: {e}")
            db.session.rollback()
            return False


# Singleton instance
cv_analyzer_service = CVAnalyzerService()
