"""Unit tests for API endpoints."""
import pytest
import json
from unittest.mock import patch, MagicMock

from services.api import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_ingestion_service():
    """Mock ingestion service."""
    with patch('services.api.ingestion_service') as mock:
        yield mock


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data


class TestAlertIngestion:
    """Tests for alert ingestion endpoint."""
    
    def test_ingest_valid_alert(self, client, mock_ingestion_service):
        """Test ingesting a valid alert."""
        mock_ingestion_service.ingest_alert.return_value = {
            "status": "success",
            "alert_id": "test-123",
            "message_id": "msg-123",
            "created_at": "2024-01-01T00:00:00"
        }
        
        alert_data = {
            "title": "Earthquake Alert",
            "message": "A 7.2 magnitude earthquake detected",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['alert_id'] == 'test-123'
    
    def test_ingest_alert_validation_error(self, client, mock_ingestion_service):
        """Test ingesting alert with validation error."""
        mock_ingestion_service.ingest_alert.side_effect = ValueError("Missing required field: title")
        
        alert_data = {
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'title' in data['message']
    
    def test_ingest_alert_non_json(self, client):
        """Test ingesting alert with non-JSON content."""
        response = client.post(
            '/api/v1/alerts',
            data='not json',
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'json' in data['message'].lower()
    
    def test_ingest_alert_internal_error(self, client, mock_ingestion_service):
        """Test handling internal errors during ingestion."""
        mock_ingestion_service.ingest_alert.side_effect = Exception("Database error")
        
        alert_data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        response = client.post(
            '/api/v1/alerts',
            data=json.dumps(alert_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestBatchIngestion:
    """Tests for batch ingestion endpoint."""
    
    def test_ingest_batch_success(self, client, mock_ingestion_service):
        """Test successful batch ingestion."""
        mock_ingestion_service.ingest_alert.side_effect = [
            {
                "status": "success",
                "alert_id": "alert-1",
                "message_id": "msg-1",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "status": "success",
                "alert_id": "alert-2",
                "message_id": "msg-2",
                "created_at": "2024-01-01T00:00:01"
            }
        ]
        
        batch_data = {
            "alerts": [
                {
                    "title": "Alert 1",
                    "message": "Message 1",
                    "alert_type": "earthquake",
                    "severity": "high"
                },
                {
                    "title": "Alert 2",
                    "message": "Message 2",
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
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['processed'] == 2
        assert data['failed'] == 0
        assert len(data['results']) == 2
    
    def test_ingest_batch_partial_failure(self, client, mock_ingestion_service):
        """Test batch ingestion with some failures."""
        mock_ingestion_service.ingest_alert.side_effect = [
            {
                "status": "success",
                "alert_id": "alert-1",
                "message_id": "msg-1",
                "created_at": "2024-01-01T00:00:00"
            },
            ValueError("Invalid data")
        ]
        
        batch_data = {
            "alerts": [
                {
                    "title": "Alert 1",
                    "message": "Message 1",
                    "alert_type": "earthquake",
                    "severity": "high"
                },
                {
                    "title": "Alert 2",
                    "message": "Message 2",
                    "alert_type": "invalid",
                    "severity": "medium"
                }
            ]
        }
        
        response = client.post(
            '/api/v1/alerts/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        assert response.status_code == 207
        data = json.loads(response.data)
        assert data['status'] == 'partial_success'
        assert data['processed'] == 1
        assert data['failed'] == 1
        assert len(data['errors']) == 1
    
    def test_ingest_batch_empty_alerts(self, client):
        """Test batch ingestion with empty alerts array."""
        batch_data = {"alerts": []}
        
        response = client.post(
            '/api/v1/alerts/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'alerts' in data['message'].lower()
    
    def test_ingest_batch_too_many_alerts(self, client):
        """Test batch ingestion with too many alerts."""
        batch_data = {
            "alerts": [
                {
                    "title": f"Alert {i}",
                    "message": f"Message {i}",
                    "alert_type": "earthquake",
                    "severity": "low"
                }
                for i in range(101)
            ]
        }
        
        response = client.post(
            '/api/v1/alerts/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert '100' in data['message']
    
    def test_ingest_batch_non_json(self, client):
        """Test batch ingestion with non-JSON content."""
        response = client.post(
            '/api/v1/alerts/batch',
            data='not json',
            content_type='text/plain'
        )
        
        assert response.status_code == 400


class TestErrorHandlers:
    """Tests for error handlers."""
    
    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()
    
    def test_405_handler(self, client):
        """Test 405 error handler."""
        response = client.put('/health')
        
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not allowed' in data['message'].lower()
