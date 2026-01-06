"""Alert ingestion service for PolyAlert.

This service receives disaster alerts from various sources and publishes them
to Pub/Sub for further processing.
"""
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from google.cloud import pubsub_v1

from core.models import Alert, AlertSeverity, AlertType, Location
from core.config import Config
from core.utils import setup_logger, sanitize_message


logger = setup_logger(__name__)


class IngestionService:
    """Service for ingesting disaster alerts."""
    
    def __init__(
        self, 
        project_id: Optional[str] = None,
        topic_name: Optional[str] = None
    ):
        """Initialize ingestion service.
        
        Args:
            project_id: GCP project ID
            topic_name: Pub/Sub topic name for alerts
        """
        self.project_id = project_id or Config.GCP_PROJECT_ID
        self.topic_name = topic_name or Config.PUBSUB_ALERT_TOPIC
        self.publisher = None
        self.topic_path = None
        
        if self.project_id and self.topic_name:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_path = self.publisher.topic_path(
                    self.project_id, 
                    self.topic_name
                )
                logger.info(f"Initialized publisher for topic: {self.topic_path}")
            except Exception as e:
                logger.warning(f"Could not initialize Pub/Sub client: {e}")
    
    def validate_alert_data(self, data: Dict) -> tuple[bool, Optional[str]]:
        """Validate incoming alert data.
        
        Args:
            data: Alert data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields
        required_fields = ["title", "message", "alert_type", "severity"]
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate alert type
        try:
            AlertType(data["alert_type"])
        except ValueError:
            valid_types = [t.value for t in AlertType]
            return False, f"Invalid alert_type. Must be one of: {valid_types}"
        
        # Validate severity
        try:
            AlertSeverity(data["severity"])
        except ValueError:
            valid_severities = [s.value for s in AlertSeverity]
            return False, f"Invalid severity. Must be one of: {valid_severities}"
        
        # Validate location if provided
        if "location" in data and data["location"]:
            location = data["location"]
            if "latitude" not in location or "longitude" not in location:
                return False, "Location must contain latitude and longitude"
            
            try:
                lat = float(location["latitude"])
                lon = float(location["longitude"])
                if not (-90 <= lat <= 90):
                    return False, "Latitude must be between -90 and 90"
                if not (-180 <= lon <= 180):
                    return False, "Longitude must be between -180 and 180"
            except (ValueError, TypeError):
                return False, "Invalid latitude or longitude values"
        
        # Validate message length
        if len(data.get("message", "")) > 5000:
            return False, "Message exceeds maximum length of 5000 characters"
        
        return True, None
    
    def process_alert(self, data: Dict) -> Alert:
        """Process and create Alert object from input data.
        
        Args:
            data: Input alert data
            
        Returns:
            Alert object
        """
        # Create location if provided
        location = None
        if "location" in data and data["location"]:
            loc_data = data["location"]
            location = Location(
                latitude=float(loc_data["latitude"]),
                longitude=float(loc_data["longitude"]),
                address=loc_data.get("address"),
                city=loc_data.get("city"),
                region=loc_data.get("region"),
                country=loc_data.get("country"),
                radius_km=float(loc_data["radius_km"]) if "radius_km" in loc_data else None,
            )
        
        # Sanitize message content
        title = sanitize_message(data["title"], max_length=200)
        message = sanitize_message(data["message"], max_length=5000)
        
        # Create alert
        alert = Alert(
            alert_type=AlertType(data["alert_type"]),
            severity=AlertSeverity(data["severity"]),
            title=title,
            message=message,
            location=location,
            source=data.get("source", "api"),
            source_language=data.get("source_language", "en"),
            target_languages=data.get("target_languages", ["en"]),
            metadata=data.get("metadata", {}),
        )
        
        # Set expiration time (default 24 hours for most alerts)
        if not alert.expires_at:
            expiry_hours = 24
            if alert.severity == AlertSeverity.CRITICAL:
                expiry_hours = 48
            elif alert.severity == AlertSeverity.INFO:
                expiry_hours = 12
            
            alert.expires_at = alert.created_at + timedelta(hours=expiry_hours)
        
        return alert
    
    def publish_alert(self, alert: Alert) -> str:
        """Publish alert to Pub/Sub topic.
        
        Args:
            alert: Alert object to publish
            
        Returns:
            Message ID from Pub/Sub
            
        Raises:
            RuntimeError: If publisher is not initialized
        """
        if not self.publisher or not self.topic_path:
            raise RuntimeError("Pub/Sub publisher not initialized")
        
        # Convert alert to JSON
        alert_data = json.dumps(alert.to_dict()).encode("utf-8")
        
        # Publish message
        future = self.publisher.publish(
            self.topic_path,
            alert_data,
            alert_id=alert.alert_id,
            severity=alert.severity.value,
            alert_type=alert.alert_type.value,
        )
        
        message_id = future.result()
        logger.info(f"Published alert {alert.alert_id} with message ID: {message_id}")
        
        return message_id
    
    def ingest_alert(self, data: Dict) -> Dict:
        """Main method to ingest an alert.
        
        Args:
            data: Alert data dictionary
            
        Returns:
            Response dictionary with alert_id and status
            
        Raises:
            ValueError: If validation fails
        """
        # Validate input data
        is_valid, error_msg = self.validate_alert_data(data)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Process alert
        alert = self.process_alert(data)
        
        # Publish to Pub/Sub
        try:
            message_id = self.publish_alert(alert)
            
            return {
                "status": "success",
                "alert_id": alert.alert_id,
                "message_id": message_id,
                "created_at": alert.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")
            raise
