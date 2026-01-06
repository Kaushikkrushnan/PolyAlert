"""Unit tests for core models."""
import pytest
from datetime import datetime, timedelta
from core.models import (
    Alert, AlertSeverity, AlertType, Location,
    Translation, Delivery, DeliveryChannel, DeliveryStatus
)


class TestLocation:
    """Tests for Location model."""
    
    def test_location_creation(self):
        """Test creating a location."""
        loc = Location(
            latitude=37.7749,
            longitude=-122.4194,
            city="San Francisco",
            region="California",
            country="USA"
        )
        
        assert loc.latitude == 37.7749
        assert loc.longitude == -122.4194
        assert loc.city == "San Francisco"
        assert loc.region == "California"
        assert loc.country == "USA"
    
    def test_location_to_dict(self):
        """Test converting location to dictionary."""
        loc = Location(
            latitude=37.7749,
            longitude=-122.4194,
            city="San Francisco"
        )
        
        data = loc.to_dict()
        
        assert data["latitude"] == 37.7749
        assert data["longitude"] == -122.4194
        assert data["city"] == "San Francisco"
        assert "address" in data


class TestAlert:
    """Tests for Alert model."""
    
    def test_alert_creation_with_defaults(self):
        """Test creating an alert with default values."""
        alert = Alert(
            title="Test Alert",
            message="This is a test alert"
        )
        
        assert alert.alert_id is not None
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.alert_type == AlertType.OTHER
        assert alert.severity == AlertSeverity.INFO
        assert alert.source_language == "en"
        assert isinstance(alert.created_at, datetime)
    
    def test_alert_creation_with_all_fields(self):
        """Test creating an alert with all fields."""
        location = Location(latitude=37.7749, longitude=-122.4194)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        alert = Alert(
            alert_type=AlertType.EARTHQUAKE,
            severity=AlertSeverity.CRITICAL,
            title="Earthquake Alert",
            message="7.2 magnitude earthquake detected",
            location=location,
            source="USGS",
            source_language="en",
            target_languages=["en", "es", "zh"],
            expires_at=expires_at,
            metadata={"magnitude": 7.2}
        )
        
        assert alert.alert_type == AlertType.EARTHQUAKE
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == "Earthquake Alert"
        assert alert.location == location
        assert alert.source == "USGS"
        assert len(alert.target_languages) == 3
        assert alert.metadata["magnitude"] == 7.2
    
    def test_alert_to_dict(self):
        """Test converting alert to dictionary."""
        alert = Alert(
            title="Test Alert",
            message="Test message",
            alert_type=AlertType.FLOOD,
            severity=AlertSeverity.HIGH
        )
        
        data = alert.to_dict()
        
        assert data["alert_id"] == alert.alert_id
        assert data["title"] == "Test Alert"
        assert data["message"] == "Test message"
        assert data["alert_type"] == "flood"
        assert data["severity"] == "high"
        assert "created_at" in data
    
    def test_alert_from_dict(self):
        """Test creating alert from dictionary."""
        data = {
            "alert_id": "test-123",
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "earthquake",
            "severity": "critical",
            "source": "test",
            "source_language": "en",
            "target_languages": ["en", "es"],
            "created_at": "2024-01-01T00:00:00",
            "metadata": {"test": True}
        }
        
        alert = Alert.from_dict(data)
        
        assert alert.alert_id == "test-123"
        assert alert.title == "Test Alert"
        assert alert.alert_type == AlertType.EARTHQUAKE
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.metadata["test"] is True
    
    def test_alert_from_dict_with_location(self):
        """Test creating alert from dictionary with location."""
        data = {
            "title": "Test Alert",
            "message": "Test message",
            "alert_type": "flood",
            "severity": "high",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "city": "San Francisco"
            }
        }
        
        alert = Alert.from_dict(data)
        
        assert alert.location is not None
        assert alert.location.latitude == 37.7749
        assert alert.location.city == "San Francisco"


class TestTranslation:
    """Tests for Translation model."""
    
    def test_translation_creation(self):
        """Test creating a translation."""
        translation = Translation(
            alert_id="alert-123",
            source_language="en",
            target_language="es",
            original_title="Earthquake Alert",
            original_message="A 7.2 magnitude earthquake detected",
            translated_title="Alerta de Terremoto",
            translated_message="Se detectó un terremoto de magnitud 7.2"
        )
        
        assert translation.translation_id is not None
        assert translation.alert_id == "alert-123"
        assert translation.source_language == "en"
        assert translation.target_language == "es"
        assert translation.translated_title == "Alerta de Terremoto"
    
    def test_translation_to_dict(self):
        """Test converting translation to dictionary."""
        translation = Translation(
            alert_id="alert-123",
            source_language="en",
            target_language="es",
            original_title="Test",
            original_message="Test message",
            translated_title="Prueba",
            translated_message="Mensaje de prueba"
        )
        
        data = translation.to_dict()
        
        assert data["alert_id"] == "alert-123"
        assert data["source_language"] == "en"
        assert data["target_language"] == "es"
        assert "translation_id" in data
        assert "created_at" in data


class TestDelivery:
    """Tests for Delivery model."""
    
    def test_delivery_creation(self):
        """Test creating a delivery record."""
        delivery = Delivery(
            alert_id="alert-123",
            channel=DeliveryChannel.SMS,
            recipient="+1234567890",
            message="Test alert message",
            status=DeliveryStatus.PENDING
        )
        
        assert delivery.delivery_id is not None
        assert delivery.alert_id == "alert-123"
        assert delivery.channel == DeliveryChannel.SMS
        assert delivery.recipient == "+1234567890"
        assert delivery.status == DeliveryStatus.PENDING
    
    def test_delivery_to_dict(self):
        """Test converting delivery to dictionary."""
        delivery = Delivery(
            alert_id="alert-123",
            channel=DeliveryChannel.WHATSAPP,
            recipient="+1234567890",
            message="Test message",
            status=DeliveryStatus.SENT
        )
        
        data = delivery.to_dict()
        
        assert data["alert_id"] == "alert-123"
        assert data["channel"] == "whatsapp"
        assert data["recipient"] == "+1234567890"
        assert data["status"] == "sent"
        assert "delivery_id" in data
