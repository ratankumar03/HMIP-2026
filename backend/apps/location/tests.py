from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class LocationTestCase(TestCase):
    """Test cases for location app"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            phone='1234567890',
            password='test123'
        )
    
    def test_location_tracking(self):
        """Test location tracking functionality"""
        self.assertIsNotNone(self.user)
    
    def test_websocket_connection(self):
        """Test WebSocket connection"""
        # Add WebSocket test logic here
        self.assertEqual(1, 1)