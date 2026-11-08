"""
Regression tests for analysis bugs fixed on 2026-11-08 (formerly known issues 1 to 4):
text cleaning gluing words, `Mid Level` vs `Mid-Level`, seniority detection, and the
constant career score.
"""
import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp_analyzer import NLPAnalyzer, AnalysisResult
from app.services.pdf_extractor import PDFExtractor
from tests.test_data.sample_cvs import ALL_SAMPLE_CVS

CANONICAL_LEVELS = {"Fresher", "Junior", "Mid-Level", "Senior", "Unknown"}


class TestCleaningKeepsSingleLetterWords(unittest.TestCase):
    """Issue 1: step 5 of _clean_and_normalize glued single-letter words to neighbours."""

    def setUp(self):
        self.extractor = PDFExtractor()

    def test_single_letter_words_survive(self):
        text = "I am a developer\nB S in CS\nWorked at a big firm"
        cleaned = self.extractor._clean_and_normalize(text)
        self.assertIn("I am a developer", cleaned)
        self.assertIn("Worked at a big firm", cleaned)
        self.assertNotIn("ama", cleaned)
        self.assertNotIn("ata", cleaned)

    def test_never_joins_across_newline(self):
        cleaned = self.extractor._clean_and_normalize("Led a team of 5\nA B testing")
        self.assertIn("Led a team of 5", cleaned)
        self.assertIn("A B testing", cleaned)

    def test_letter_spaced_runs_still_collapse(self):
        cleaned = self.extractor._clean_and_normalize("Skills: J a v a and P y t h o n")
        self.assertEqual(cleaned, "Skills: Java and Python")


class TestExperienceLevelLabels(unittest.TestCase):
    """Issue 2: the keyword path returned 'Mid Level', the year path 'Mid-Level'."""

    @classmethod
    def setUpClass(cls):
        cls.analyzer = NLPAnalyzer()

    def test_mid_level_keyword_returns_canonical_label(self):
        text = (
            "ALEX DOE\nMid level software developer building web services in Python and SQL.\n\n"
            "SKILLS\nPython, SQL, Docker, Git, Linux\n"
        )
        result = self.analyzer.analyze(text)
        self.assertEqual(result.experience_level, "Mid-Level")
        self.assertEqual(result.experience_score, 80)

    def test_every_sample_gets_a_canonical_label(self):
        for name, sample in ALL_SAMPLE_CVS.items():
            with self.subTest(cv=name):
                level = self.analyzer.analyze(sample["text"]).experience_level
                self.assertIn(level, CANONICAL_LEVELS)


class TestSeniorityDetection(unittest.TestCase):
    """Issue 3: substring keywords, junior before senior, current_year hard-coded to 2024."""

    @classmethod
    def setUpClass(cls):
        cls.analyzer = NLPAnalyzer()

    def test_graduated_and_associate_do_not_override_dates(self):
        text = (
            "JANE ROE\nBackend Engineer\n\n"
            "WORK EXPERIENCE\n"
            "Backend Engineer | Acme Corp | 2016 - Present\n"
            "• Built the payments platform used by 2 million customers\n"
            "• Designed services in Python and PostgreSQL\n\n"
            "EDUCATION\n"
            "Associate degree in Computing, graduated 2015\n"
        )
        self.assertEqual(self.analyzer.analyze(text).experience_level, "Senior")

    def test_present_uses_the_real_current_year(self):
        start = datetime.date.today().year - 4
        text = (
            "SAM LEE\nSoftware Developer\n\n"
            "WORK EXPERIENCE\n"
            f"Software Developer | Foo Ltd | {start} - Present\n"
            "• Built internal tools in Python\n"
            "• Maintained the billing database\n"
        )
        self.assertEqual(self.analyzer.analyze(text).experience_level, "Mid-Level")

    def test_senior_keyword_beats_junior_keyword(self):
        text = (
            "PAT KIM\nSenior developer, previously a junior developer at a small agency.\n\n"
            "SKILLS\nJavaScript, React, Node.js, CSS, HTML\n"
        )
        self.assertEqual(self.analyzer.analyze(text).experience_level, "Senior")

    def test_keywords_need_word_boundaries(self):
        # "leadership" must not count as "lead", "associated" not as "associate"
        text = (
            "KIM PARK\nAnalyst with strong leadership skills, associated with several charities.\n\n"
            "SKILLS\nExcel, SQL, Tableau, Python, Statistics\n"
        )
        self.assertEqual(self.analyzer.analyze(text).experience_level, "Unknown")

    def test_samples_detect_expected_level(self):
        for name, sample in ALL_SAMPLE_CVS.items():
            with self.subTest(cv=name):
                level = self.analyzer.analyze(sample["text"]).experience_level
                self.assertEqual(level, sample["expected"]["experience_level"])


class TestCareerScore(unittest.TestCase):
    """Issue 4: career score was a constant 70."""

    @classmethod
    def setUpClass(cls):
        cls.analyzer = NLPAnalyzer()

    def _career(self, field, skills):
        result = AnalysisResult(career_field=field, skills_found=skills)
        return self.analyzer._calculate_scores("some text", result)["career"]

    def test_general_scores_50(self):
        self.assertEqual(self._career("General", ["python", "excel"]), 50)

    def test_matching_skills_add_5_each(self):
        # python, pandas and numpy are in Data Science's lists; java is not
        self.assertEqual(self._career("Data Science", ["python", "pandas", "numpy", "java"]), 85)

    def test_detected_field_without_matches_scores_70(self):
        self.assertEqual(self._career("Data Science", ["photoshop"]), 70)

    def test_capped_at_100(self):
        skills = ["python", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn",
                  "plotly", "jupyter", "statistics", "data visualization"]
        self.assertEqual(self._career("Data Science", skills), 100)

    def test_no_career_focus_strength_for_general(self):
        result = AnalysisResult(career_field="General")
        strengths = self.analyzer._identify_strengths(result)
        self.assertFalse(any("career focus" in s for s in strengths))


if __name__ == "__main__":
    unittest.main(verbosity=2)
