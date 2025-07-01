from django.test import TestCase, Client
from django.urls import reverse
import json

class HealthCheckTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_health_check_endpoint(self):
        """Test that the health check endpoint returns a 200 status code and correct data"""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains the expected keys
        self.assertIn('status', data)
        self.assertIn('database', data)
        
        # Check that the status is healthy
        self.assertEqual(data['status'], 'healthy')
        
        # Database should be healthy in test environment
        self.assertEqual(data['database'], 'healthy')