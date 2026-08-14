"""
IntelliCV Accuracy Validator
Comprehensive accuracy testing and reporting for NLP analysis results.
"""
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp_analyzer import NLPAnalyzer
from tests.test_data.sample_cvs import ALL_SAMPLE_CVS


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    details: str = ""


@dataclass
class CVValidationReport:
    """Validation report for a single CV"""
    cv_name: str
    overall_passed: bool
    score: float
    expected_score_range: str
    experience_level: str
    expected_experience_level: str
    career_field: str
    expected_career_field: str
    skills_found: int
    required_skills_found: int
    total_required_skills: int
    sections_detected: List[str]
    validation_results: List[ValidationResult]


class AccuracyValidator:
    """
    Comprehensive accuracy validation for IntelliCV NLP analysis.
    Validates scoring, career detection, experience level, and skill extraction.
    """
    
    def __init__(self):
        self.analyzer = NLPAnalyzer()
        self.reports: List[CVValidationReport] = []
        
        # Acceptable career field alternatives
        self.career_alternatives = {
            "Data Science": ["Machine Learning", "Data Analytics", "Artificial Intelligence", "Data Engineering"],
            "Machine Learning": ["Data Science", "Artificial Intelligence", "NLP Engineer", "Computer Vision"],
            "Information Technology": ["Software Engineering", "Data Engineering", "Cybersecurity"],
            "Accountant": ["Finance", "Banking"],
            "Healthcare": ["Medical", "Nursing"],
            "Marketing": ["Digital Media", "Business Development"],
            "General": ["Unknown", "Teacher"]  # Poor CVs may be misclassified
        }
        
        # Experience level equivalents
        self.experience_equivalents = {
            "Senior": ["Senior"],
            "Mid-Level": ["Mid-Level", "Mid Level"],
            "Junior": ["Junior"],
            "Fresher": ["Fresher", "Entry"],
            "Entry": ["Fresher", "Entry"],
            "Unknown": ["Unknown"]
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """Run validation on all sample CVs and generate report"""
        self.reports = []
        
        for cv_name, sample in ALL_SAMPLE_CVS.items():
            report = self._validate_cv(cv_name, sample)
            self.reports.append(report)
        
        return self._generate_summary()
    
    def _validate_cv(self, cv_name: str, sample: Dict) -> CVValidationReport:
        """Validate a single CV against expected results"""
        result = self.analyzer.analyze(sample["text"])
        expected = sample["expected"]
        
        validations = []
        
        # 1. Validate score range
        score_passed = expected["min_score"] <= result.overall_score <= expected["max_score"]
        validations.append(ValidationResult(
            test_name="Score Range",
            passed=score_passed,
            expected=f"{expected['min_score']}-{expected['max_score']}",
            actual=result.overall_score,
            details=f"Score {'within' if score_passed else 'outside'} expected range"
        ))
        
        # 2. Validate career field
        acceptable_fields = [expected["career_field"]] + self.career_alternatives.get(expected["career_field"], [])
        career_passed = result.career_field in acceptable_fields
        validations.append(ValidationResult(
            test_name="Career Field",
            passed=career_passed,
            expected=expected["career_field"],
            actual=result.career_field,
            details=f"Acceptable fields: {acceptable_fields}"
        ))
        
        # 3. Validate experience level
        expected_exp = expected["experience_level"]
        acceptable_exp = self.experience_equivalents.get(expected_exp, [expected_exp])
        exp_passed = result.experience_level in acceptable_exp
        validations.append(ValidationResult(
            test_name="Experience Level",
            passed=exp_passed,
            expected=expected["experience_level"],
            actual=result.experience_level,
            details=f"Acceptable: {acceptable_exp}"
        ))
        
        # 4. Validate required sections detected
        required_sections = expected.get("required_sections", [])
        detected_sections = [name for name, section in result.sections.items() if section.detected]
        
        missing_sections = [s for s in required_sections if s not in detected_sections]
        sections_passed = len(missing_sections) == 0
        validations.append(ValidationResult(
            test_name="Section Detection",
            passed=sections_passed,
            expected=required_sections,
            actual=detected_sections,
            details=f"Missing: {missing_sections}" if missing_sections else "All required sections found"
        ))
        
        # 5. Validate required skills found
        required_skills = expected.get("required_skills", [])
        skills_lower = [s.lower() for s in result.skills_found]
        found_required = [s for s in required_skills if s.lower() in skills_lower]
        
        skills_passed = len(found_required) >= len(required_skills) * 0.7  # 70% threshold
        validations.append(ValidationResult(
            test_name="Skill Extraction",
            passed=skills_passed,
            expected=required_skills,
            actual=found_required,
            details=f"Found {len(found_required)}/{len(required_skills)} required skills"
        ))
        
        # Calculate overall pass
        overall_passed = all(v.passed for v in validations)
        
        return CVValidationReport(
            cv_name=cv_name,
            overall_passed=overall_passed,
            score=result.overall_score,
            expected_score_range=f"{expected['min_score']}-{expected['max_score']}",
            experience_level=result.experience_level,
            expected_experience_level=expected["experience_level"],
            career_field=result.career_field,
            expected_career_field=expected["career_field"],
            skills_found=len(result.skills_found),
            required_skills_found=len(found_required),
            total_required_skills=len(required_skills),
            sections_detected=detected_sections,
            validation_results=validations
        )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from validation reports"""
        total = len(self.reports)
        passed = sum(1 for r in self.reports if r.overall_passed)
        
        # Calculate accuracy for each metric
        score_accuracy = sum(1 for r in self.reports 
                           for v in r.validation_results 
                           if v.test_name == "Score Range" and v.passed) / total * 100
        
        career_accuracy = sum(1 for r in self.reports 
                             for v in r.validation_results 
                             if v.test_name == "Career Field" and v.passed) / total * 100
        
        exp_accuracy = sum(1 for r in self.reports 
                          for v in r.validation_results 
                          if v.test_name == "Experience Level" and v.passed) / total * 100
        
        section_accuracy = sum(1 for r in self.reports 
                              for v in r.validation_results 
                              if v.test_name == "Section Detection" and v.passed) / total * 100
        
        skill_accuracy = sum(1 for r in self.reports 
                            for v in r.validation_results 
                            if v.test_name == "Skill Extraction" and v.passed) / total * 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_cvs_tested": total,
            "overall_pass_rate": f"{passed}/{total} ({passed/total*100:.1f}%)",
            "accuracy_by_metric": {
                "score_range": f"{score_accuracy:.1f}%",
                "career_field": f"{career_accuracy:.1f}%",
                "experience_level": f"{exp_accuracy:.1f}%",
                "section_detection": f"{section_accuracy:.1f}%",
                "skill_extraction": f"{skill_accuracy:.1f}%"
            },
            "average_accuracy": f"{(score_accuracy + career_accuracy + exp_accuracy + section_accuracy + skill_accuracy) / 5:.1f}%",
            "detailed_reports": [self._report_to_dict(r) for r in self.reports]
        }
    
    def _report_to_dict(self, report: CVValidationReport) -> Dict:
        """Convert report to dictionary for JSON serialization"""
        return {
            "cv_name": report.cv_name,
            "overall_passed": report.overall_passed,
            "score": report.score,
            "expected_score_range": report.expected_score_range,
            "experience_level": report.experience_level,
            "expected_experience_level": report.expected_experience_level,
            "career_field": report.career_field,
            "expected_career_field": report.expected_career_field,
            "skills_found": report.skills_found,
            "required_skills_found": report.required_skills_found,
            "total_required_skills": report.total_required_skills,
            "sections_detected": report.sections_detected,
            "validation_results": [asdict(v) for v in report.validation_results]
        }
    
    def print_report(self):
        """Print formatted validation report to console"""
        summary = self._generate_summary()
        
        print("\n" + "="*80)
        print("  INTELLICV NLP ACCURACY VALIDATION REPORT")
        print("="*80)
        print(f"  Generated: {summary['timestamp']}")
        print(f"  Total CVs Tested: {summary['total_cvs_tested']}")
        print(f"  Overall Pass Rate: {summary['overall_pass_rate']}")
        print(f"  Average Accuracy: {summary['average_accuracy']}")
        print("="*80)
        
        print("\n📊 ACCURACY BY METRIC:")
        print("-"*40)
        for metric, accuracy in summary['accuracy_by_metric'].items():
            status = "✅" if float(accuracy.replace('%', '')) >= 70 else "⚠️"
            print(f"  {status} {metric.replace('_', ' ').title()}: {accuracy}")
        
        print("\n📋 DETAILED CV RESULTS:")
        print("-"*80)
        
        for report in self.reports:
            status = "✅ PASS" if report.overall_passed else "❌ FAIL"
            print(f"\n  [{status}] {report.cv_name}")
            print(f"      Score: {report.score} (expected: {report.expected_score_range})")
            print(f"      Career: {report.career_field} (expected: {report.expected_career_field})")
            print(f"      Experience: {report.experience_level} (expected: {report.expected_experience_level})")
            print(f"      Skills: {report.required_skills_found}/{report.total_required_skills} required found")
            
            # Show failed validations
            failed = [v for v in report.validation_results if not v.passed]
            if failed:
                print(f"      ⚠️ Issues:")
                for v in failed:
                    print(f"         - {v.test_name}: expected '{v.expected}', got '{v.actual}'")
        
        print("\n" + "="*80)
        print("  END OF REPORT")
        print("="*80 + "\n")
        
        return summary
    
    def save_report(self, filepath: str):
        """Save validation report to JSON file"""
        summary = self._generate_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Report saved to: {filepath}")


def run_validation():
    """Run full validation and print report"""
    validator = AccuracyValidator()
    validator.validate_all()
    summary = validator.print_report()
    
    # Save report
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'tests',
        'reports',
        f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    
    # Create reports directory if needed
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    validator.save_report(report_path)
    
    return summary


if __name__ == '__main__':
    run_validation()
