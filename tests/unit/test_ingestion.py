"""Unit tests for ingestion service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.ingestion import IngestionService
from core.models import Alert, AlertSeverity, AlertType, Location


class TestIngestionServiceValidation:
    """Tests for alert validation."""
    
    @pytest.fixture
    def service(self):
        """Create ingestion service without Pub/Sub."""
        with patch('services.ingestion.pubsub_v1'):
            return IngestionService(project_id=None, topic_name=None)
    
    def test_validate_valid_alert(self, service):
        """Test validating a valid alert."""
        data = {
            "title": "Earthquake Alert",
            "message": "A 7.2 magnitude earthquake detected",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is True
        assert error is None
    
    def test_validate_missing_title(self, service):
        """Test validation fails for missing title."""
        data = {
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "title" in error
    
    def test_validate_missing_message(self, service):
        """Test validation fails for missing message."""
        data = {
            "title": "Test Alert",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "message" in error
    
    def test_validate_invalid_alert_type(self, service):
        """Test validation fails for invalid alert type."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "invalid_type",
            "severity": "critical"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "alert_type" in error
    
    def test_validate_invalid_severity(self, service):
        """Test validation fails for invalid severity."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "invalid_severity"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "severity" in error
    
    def test_validate_location_missing_coordinates(self, service):
        """Test validation fails for location without coordinates."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical",
            "location": {
                "city": "San Francisco"
            }
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "latitude" in error or "longitude" in error
    
    def test_validate_invalid_latitude(self, service):
        """Test validation fails for invalid latitude."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical",
            "location": {
                "latitude": 200,
                "longitude": 0
            }
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "Latitude" in error
    
    def test_validate_invalid_longitude(self, service):
        """Test validation fails for invalid longitude."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical",
            "location": {
                "latitude": 0,
                "longitude": 200
            }
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "Longitude" in error
    
    def test_validate_message_too_long(self, service):
        """Test validation fails for message exceeding max length."""
        data = {
            "title": "Test Alert",
            "message": "x" * 6000,
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        is_valid, error = service.validate_alert_data(data)
        assert is_valid is False
        assert "length" in error


class TestIngestionServiceProcessing:
    """Tests for alert processing."""
    
    @pytest.fixture
    def service(self):
        """Create ingestion service without Pub/Sub."""
        with patch('services.ingestion.pubsub_v1'):
            return IngestionService(project_id=None, topic_name=None)
    
    def test_process_basic_alert(self, service):
        """Test processing a basic alert."""
        data = {
            "title": "Earthquake Alert",
            "message": "A 7.2 magnitude earthquake detected",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        alert = service.process_alert(data)
        
        assert isinstance(alert, Alert)
        assert alert.title == "Earthquake Alert"
        assert alert.alert_type == AlertType.EARTHQUAKE
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.alert_id is not None
        assert alert.expires_at is not None
    
    def test_process_alert_with_location(self, service):
        """Test processing alert with location."""
        data = {
            "title": "Flood Warning",
            "message": "Flash flood warning in effect",
            "alert_type": "flood",
            "severity": "high",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "city": "San Francisco",
                "region": "California"
            }
        }
        
        alert = service.process_alert(data)
        
        assert alert.location is not None
        assert alert.location.latitude == 37.7749
        assert alert.location.longitude == -122.4194
        assert alert.location.city == "San Francisco"
    
    def test_process_alert_sanitizes_message(self, service):
        """Test that message content is sanitized."""
        data = {
            "title": "  Test   Alert  ",
            "message": "Test   message   with   extra   spaces",
            "alert_type": "fire",
            "severity": "medium"
        }
        
        alert = service.process_alert(data)
        
        assert "  " not in alert.title
        assert "  " not in alert.message
    
    def test_process_alert_sets_expiration(self, service):
        """Test that expiration time is set based on severity."""
        data_critical = {
            "title": "Critical Alert",
            "message": "Critical message",
            "alert_type": "earthquake",
            "severity": "critical"
        }
        
        data_info = {
            "title": "Info Alert",
            "message": "Info message",
            "alert_type": "earthquake",
            "severity": "info"
        }
        
        alert_critical = service.process_alert(data_critical)
        alert_info = service.process_alert(data_info)
        
        # Critical alerts expire later than info alerts
        assert alert_critical.expires_at > alert_info.expires_at


class TestIngestionServicePublishing:
    """Tests for alert publishing."""
    
    @pytest.fixture
    def service_with_pubsub(self):
        """Create ingestion service with mocked Pub/Sub."""
        with patch('services.ingestion.pubsub_v1.PublisherClient') as mock_publisher:
            mock_client = MagicMock()
            mock_publisher.return_value = mock_client
            mock_client.topic_path.return_value = "projects/test/topics/alerts"
            
            # Mock the publish method
            future = MagicMock()
            future.result.return_value = "message-123"
            mock_client.publish.return_value = future
            
            service = IngestionService(
                project_id="test-project",
                topic_name="test-topic"
            )
            service.publisher = mock_client
            
            return service
    
    def test_publish_alert(self, service_with_pubsub):
        """Test publishing an alert to Pub/Sub."""
        alert = Alert(
            title="Test Alert",
            message="Test message",
            alert_type=AlertType.EARTHQUAKE,
            severity=AlertSeverity.HIGH
        )
        
        message_id = service_with_pubsub.publish_alert(alert)
        
        assert message_id == "message-123"
        assert service_with_pubsub.publisher.publish.called
    
    def test_publish_alert_without_publisher(self):
        """Test publishing without initialized publisher raises error."""
        with patch('services.ingestion.pubsub_v1'):
            service = IngestionService(project_id=None, topic_name=None)
            # Explicitly set publisher to None to test error handling
            service.publisher = None
            service.topic_path = None
            alert = Alert(title="Test", message="Test")
            
            with pytest.raises(RuntimeError):
                service.publish_alert(alert)
    
    def test_ingest_alert_end_to_end(self, service_with_pubsub):
        """Test complete ingestion flow."""
        data = {
            "title": "Earthquake Alert",
            "message": "A 7.2 magnitude earthquake detected",
            "alert_type": "earthquake",
            "severity": "critical",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        }
        
        result = service_with_pubsub.ingest_alert(data)
        
        assert result["status"] == "success"
        assert "alert_id" in result
        assert result["message_id"] == "message-123"
        assert "created_at" in result
    
    def test_ingest_invalid_alert_raises_error(self, service_with_pubsub):
        """Test ingesting invalid alert raises ValueError."""
        data = {
            "title": "Test Alert",
            # Missing required fields
        }
        
        with pytest.raises(ValueError):
            service_with_pubsub.ingest_alert(data)
