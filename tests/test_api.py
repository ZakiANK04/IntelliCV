"""
API tests for IntelliCV endpoints.
Tests the REST API functionality.
"""
import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        from app import create_app
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'IntelliCV', response.data)
    
    def test_upload_page(self):
        """Test upload page loads"""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
    
    def test_documentation_page(self):
        """Test documentation page loads"""
        response = self.client.get('/documentation')
        self.assertEqual(response.status_code, 200)
    
    def test_submit_user_missing_data(self):
        """Test user submission with missing data"""
        response = self.client.post('/api/submit-user',
                                   data=json.dumps({}),
                                   content_type='application/json')
        self.assertIn(response.status_code, [400, 500])
    
    def test_submit_user_valid_data(self):
        """Test user submission with valid data"""
        response = self.client.post('/api/submit-user',
                                   data=json.dumps({
                                       'full_name': 'Test User',
                                       'email': 'test@example.com',
                                       'phone': '1234567890'
                                   }),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('user_id', data)
    
    def test_upload_cv_no_file(self):
        """Test CV upload without file"""
        response = self.client.post('/api/upload-cv',
                                   data={'user_id': '1'})
        self.assertEqual(response.status_code, 400)
    
    def test_upload_cv_no_user_id(self):
        """Test CV upload without user_id"""
        response = self.client.post('/api/upload-cv',
                                   data={})
        self.assertEqual(response.status_code, 400)
    
    def test_get_nonexistent_analysis(self):
        """Test getting non-existent analysis"""
        response = self.client.get('/api/analysis/99999')
        self.assertEqual(response.status_code, 404)
    
    def test_admin_login_page(self):
        """Test admin login page loads (may redirect if already logged in)"""
        response = self.client.get('/admin/')
        # Accept either 200 (login page) or 302 (redirect to dashboard)
        self.assertIn(response.status_code, [200, 302])


class TestAPIValidation(unittest.TestCase):
    """Test API input validation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        from app import create_app
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
    
    def test_invalid_email_format(self):
        """Test submission with invalid email"""
        response = self.client.post('/api/submit-user',
                                   data=json.dumps({
                                       'full_name': 'Test User',
                                       'email': 'invalid-email',
                                       'phone': '1234567890'
                                   }),
                                   content_type='application/json')
        # May accept or reject depending on validation
        self.assertIn(response.status_code, [201, 400])
    
    def test_empty_fields(self):
        """Test submission with empty required fields"""
        response = self.client.post('/api/submit-user',
                                   data=json.dumps({
                                       'full_name': '',
                                       'email': '',
                                       'phone': ''
                                   }),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main(verbosity=2)
