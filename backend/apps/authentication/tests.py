from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Test cases for authentication app"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'phone': '1234567890',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'testpass123'
        }
    
    def test_user_creation(self):
        """Test creating a new user"""
        user = User.objects.create_user(
            phone=self.user_data['phone'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(user.phone, '1234567890')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_login(self):
        """Test user login functionality"""
        user = User.objects.create_user(
            phone=self.user_data['phone'],
            password=self.user_data['password']
        )
        self.assertTrue(user.check_password('testpass123'))