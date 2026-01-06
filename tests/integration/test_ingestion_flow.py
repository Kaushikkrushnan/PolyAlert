"""Integration tests for ingestion flow."""
import pytest
import json
from unittest.mock import patch, MagicMock, call
from datetime import datetime

from services.ingestion import IngestionService
from services.api import app
from core.models import AlertType, AlertSeverity


@pytest.fixture
def mock_pubsub():
    """Mock Pub/Sub client."""
    with patch('services.ingestion.pubsub_v1.PublisherClient') as mock:
        client = MagicMock()
        mock.return_value = client
        client.topic_path.return_value = "projects/test/topics/alerts"
        
        future = MagicMock()
        future.result.return_value = "message-123"
        client.publish.return_value = future
        
        yield client


@pytest.fixture
def client(mock_pubsub):
    """Create test client with mocked ingestion service."""
    app.config['TESTING'] = True
    
    # Patch the ingestion service at module level
    with patch('services.api.ingestion_service') as mock_service:
        # Create a real ingestion service with mocked pubsub
        real_service = IngestionService(
            project_id="test-project",
            topic_name="test-topic"
        )
        real_service.publisher = mock_pubsub
        real_service.topic_path = "projects/test/topics/alerts"
        
        # Replace the mock with our configured service
        mock_service.validate_alert_data = real_service.validate_alert_data
        mock_service.process_alert = real_service.process_alert
        mock_service.publish_alert = real_service.publish_alert
        mock_service.ingest_alert = real_service.ingest_alert
        
        with app.test_client() as client:
            yield client


class TestIngestionIntegration:
    """Integration tests for the complete ingestion flow."""
    
    def test_end_to_end_ingestion(self, client, mock_pubsub):
        """Test complete flow from API to Pub/Sub."""
        alert_data = {
            "title": "Earthquake Alert",
            "message": "A 7.2 magnitude earthquake has been detected near San Francisco",
            "alert_type": "earthquake",
            "severity": "critical",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "city": "San Francisco",
                "region": "California",
                "country": "USA"
            },
            "source": "USGS",
            "source_language": "en",
            "target_languages": ["en", "es", "zh", "hi"],
            "metadata": {
                "magnitude": 7.2,
                "depth_km": 10
            }
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        # Verify API response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'alert_id' in data
        assert 'message_id' in data
        
        # Verify Pub/Sub was called
        assert mock_pubsub.publish.called
        
        # Get the published message
        call_args = mock_pubsub.publish.call_args
        published_data = json.loads(call_args[0][1].decode('utf-8'))
        
        # Verify published data
        assert published_data['title'] == alert_data['title']
        assert published_data['alert_type'] == 'earthquake'
        assert published_data['severity'] == 'critical'
        assert published_data['location']['latitude'] == 37.7749
        assert published_data['metadata']['magnitude'] == 7.2
    
    def test_batch_ingestion_integration(self, client, mock_pubsub):
        """Test batch ingestion flow."""
        batch_data = {
            "alerts": [
                {
                    "title": "Flood Warning",
                    "message": "Flash flood warning in effect",
                    "alert_type": "flood",
                    "severity": "high",
                    "location": {
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "city": "New York"
                    }
                },
                {
                    "title": "Fire Alert",
                    "message": "Wildfire approaching residential area",
                    "alert_type": "fire",
                    "severity": "critical",
                    "location": {
                        "latitude": 34.0522,
                        "longitude": -118.2437,
                        "city": "Los Angeles"
                    }
                },
                {
                    "title": "Storm Warning",
                    "message": "Severe thunderstorm warning",
                    "alert_type": "storm",
                    "severity": "medium",
                    "location": {
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "city": "Chicago"
                    }
                }
            ]
        }
        
        response = client.post(
            '/api/v1/alerts/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['processed'] == 3
        assert data['failed'] == 0
        assert len(data['results']) == 3
        
        # Verify all alerts were published
        assert mock_pubsub.publish.call_count == 3
    
    def test_validation_error_handling(self, client, mock_pubsub):
        """Test that validation errors prevent publishing."""
        invalid_alert = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "invalid_type",
            "severity": "critical"
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(invalid_alert),
            content_type='application/json'
        )
        
        # Verify error response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        
        # Verify nothing was published
        assert not mock_pubsub.publish.called
    
    def test_mixed_batch_results(self, client, mock_pubsub):
        """Test batch with both valid and invalid alerts."""
        batch_data = {
            "alerts": [
                {
                    "title": "Valid Alert",
                    "message": "This is valid",
                    "alert_type": "earthquake",
                    "severity": "high"
                },
                {
                    "title": "Invalid Alert",
                    "message": "This is invalid",
                    "alert_type": "invalid_type",
                    "severity": "high"
                },
                {
                    "title": "Another Valid Alert",
                    "message": "This is also valid",
                    "alert_type": "flood",
                    "severity": "medium"
                }
            ]
        }
        
        response = client.post(
            '/api/v1/alerts/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # Verify partial success
        assert response.status_code == 207
        data = json.loads(response.data)
        assert data['status'] == 'partial_success'
        assert data['processed'] == 2
        assert data['failed'] == 1
        
        # Verify only valid alerts were published
        assert mock_pubsub.publish.call_count == 2
    
    def test_message_sanitization_integration(self, client, mock_pubsub):
        """Test that messages are sanitized during ingestion."""
        alert_data = {
            "title": "  Alert   with   extra   spaces  ",
            "message": "Message  \n\n  with  whitespace\nissues",
            "alert_type": "earthquake",
            "severity": "high"
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # Get published message
        call_args = mock_pubsub.publish.call_args
        published_data = json.loads(call_args[0][1].decode('utf-8'))
        
        # Verify sanitization
        assert "  " not in published_data['title']
        assert "  " not in published_data['message']
    
    def test_location_data_preservation(self, client, mock_pubsub):
        """Test that location data is preserved correctly."""
        alert_data = {
            "title": "Location Test",
            "message": "Testing location data",
            "alert_type": "earthquake",
            "severity": "high",
            "location": {
                "latitude": 35.6762,
                "longitude": 139.6503,
                "address": "Tokyo Tower",
                "city": "Tokyo",
                "region": "Kanto",
                "country": "Japan",
                "radius_km": 50.0
            }
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # Get published message
        call_args = mock_pubsub.publish.call_args
        published_data = json.loads(call_args[0][1].decode('utf-8'))
        
        # Verify location data
        location = published_data['location']
        assert location['latitude'] == 35.6762
        assert location['longitude'] == 139.6503
        assert location['city'] == 'Tokyo'
        assert location['country'] == 'Japan'
        assert location['radius_km'] == 50.0
    
    def test_metadata_preservation(self, client, mock_pubsub):
        """Test that metadata is preserved during ingestion."""
        alert_data = {
            "title": "Metadata Test",
            "message": "Testing metadata",
            "alert_type": "earthquake",
            "severity": "high",
            "metadata": {
                "magnitude": 6.5,
                "depth_km": 15,
                "source_url": "https://example.com/alert",
                "custom_field": "custom_value"
            }
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # Get published message
        call_args = mock_pubsub.publish.call_args
        published_data = json.loads(call_args[0][1].decode('utf-8'))
        
        # Verify metadata
        metadata = published_data['metadata']
        assert metadata['magnitude'] == 6.5
        assert metadata['depth_km'] == 15
        assert metadata['custom_field'] == 'custom_value'
