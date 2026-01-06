"""Utility functions for PolyAlert."""
import logging
import re
from typing import Optional
import phonenumbers


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with standard configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_message(message: str, max_length: Optional[int] = None) -> str:
    """Sanitize message content."""
    # Remove excessive whitespace
    sanitized = ' '.join(message.split())
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized


def format_coordinates(latitude: float, longitude: float) -> str:
    """Format coordinates as string."""
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"
    return f"{abs(latitude):.4f}°{lat_dir}, {abs(longitude):.4f}°{lon_dir}"
