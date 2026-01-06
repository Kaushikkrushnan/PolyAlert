"""Configuration management for PolyAlert."""
import os
from typing import Optional


class Config:
    """Application configuration."""
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Google Cloud Project
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "polyalert-project")
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")
    
    # Pub/Sub
    PUBSUB_ALERT_TOPIC = os.getenv("PUBSUB_ALERT_TOPIC", "alert-ingestion")
    PUBSUB_TRANSLATION_TOPIC = os.getenv("PUBSUB_TRANSLATION_TOPIC", "alert-translation")
    PUBSUB_DELIVERY_TOPIC = os.getenv("PUBSUB_DELIVERY_TOPIC", "alert-delivery")
    
    # Firestore
    FIRESTORE_ALERTS_COLLECTION = os.getenv("FIRESTORE_ALERTS_COLLECTION", "alerts")
    FIRESTORE_TRANSLATIONS_COLLECTION = os.getenv("FIRESTORE_TRANSLATIONS_COLLECTION", "translations")
    FIRESTORE_DELIVERIES_COLLECTION = os.getenv("FIRESTORE_DELIVERIES_COLLECTION", "deliveries")
    
    # Translation API
    TRANSLATION_API_ENABLED = os.getenv("TRANSLATION_API_ENABLED", "true").lower() == "true"
    
    # API Configuration
    API_PORT = int(os.getenv("API_PORT", "8080"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    
    # Security
    API_KEY_HEADER = "X-API-Key"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return getattr(cls, key, default)
