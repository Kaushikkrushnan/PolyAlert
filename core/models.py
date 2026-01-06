"""Data models for PolyAlert system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, Enum):
    """Types of disaster alerts."""
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    STORM = "storm"
    TSUNAMI = "tsunami"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    LANDSLIDE = "landslide"
    VOLCANO = "volcano"
    OTHER = "other"


class DeliveryChannel(str, Enum):
    """Delivery channels for alerts."""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    EMAIL = "email"


class DeliveryStatus(str, Enum):
    """Status of alert delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    QUEUED = "queued"


@dataclass
class Location:
    """Geographic location information."""
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    radius_km: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "radius_km": self.radius_km,
        }


@dataclass
class Alert:
    """Disaster alert data model."""
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    alert_type: AlertType = AlertType.OTHER
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = ""
    message: str = ""
    location: Optional[Location] = None
    source: str = "unknown"
    source_language: str = "en"
    target_languages: List[str] = field(default_factory=lambda: ["en"])
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "location": self.location.to_dict() if self.location else None,
            "source": self.source,
            "source_language": self.source_language,
            "target_languages": self.target_languages,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Alert":
        """Create Alert from dictionary."""
        location_data = data.get("location")
        location = Location(**location_data) if location_data else None
        
        return cls(
            alert_id=data.get("alert_id", str(uuid4())),
            alert_type=AlertType(data.get("alert_type", "other")),
            severity=AlertSeverity(data.get("severity", "info")),
            title=data.get("title", ""),
            message=data.get("message", ""),
            location=location,
            source=data.get("source", "unknown"),
            source_language=data.get("source_language", "en"),
            target_languages=data.get("target_languages", ["en"]),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class Translation:
    """Translation data model."""
    translation_id: str = field(default_factory=lambda: str(uuid4()))
    alert_id: str = ""
    source_language: str = "en"
    target_language: str = "en"
    original_title: str = ""
    original_message: str = ""
    translated_title: str = ""
    translated_message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "translation_id": self.translation_id,
            "alert_id": self.alert_id,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "original_title": self.original_title,
            "original_message": self.original_message,
            "translated_title": self.translated_title,
            "translated_message": self.translated_message,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Delivery:
    """Delivery record data model."""
    delivery_id: str = field(default_factory=lambda: str(uuid4()))
    alert_id: str = ""
    translation_id: Optional[str] = None
    channel: DeliveryChannel = DeliveryChannel.SMS
    recipient: str = ""
    status: DeliveryStatus = DeliveryStatus.PENDING
    message: str = ""
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "delivery_id": self.delivery_id,
            "alert_id": self.alert_id,
            "translation_id": self.translation_id,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "status": self.status.value,
            "message": self.message,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }
