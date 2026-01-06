"""Unit tests for core utilities."""
import pytest
from core.utils import (
    validate_phone_number,
    validate_email,
    sanitize_message,
    format_coordinates,
    setup_logger
)
import logging


class TestPhoneValidation:
    """Tests for phone number validation."""
    
    def test_valid_us_phone(self):
        """Test valid US phone number."""
        assert validate_phone_number("+14155552671")
    
    def test_valid_international_phone(self):
        """Test valid international phone numbers."""
        assert validate_phone_number("+447911123456")  # UK
        assert validate_phone_number("+919876543210")  # India
    
    def test_invalid_phone(self):
        """Test invalid phone numbers."""
        assert not validate_phone_number("123")
        assert not validate_phone_number("invalid")
        assert not validate_phone_number("")


class TestEmailValidation:
    """Tests for email validation."""
    
    def test_valid_emails(self):
        """Test valid email addresses."""
        assert validate_email("test@example.com")
        assert validate_email("user.name+tag@example.co.uk")
        assert validate_email("test123@test-domain.com")
    
    def test_invalid_emails(self):
        """Test invalid email addresses."""
        assert not validate_email("invalid")
        assert not validate_email("@example.com")
        assert not validate_email("test@")
        assert not validate_email("test @example.com")
        assert not validate_email("")


class TestMessageSanitization:
    """Tests for message sanitization."""
    
    def test_sanitize_whitespace(self):
        """Test removing excessive whitespace."""
        message = "Test   message  with    extra   spaces"
        result = sanitize_message(message)
        assert result == "Test message with extra spaces"
    
    def test_sanitize_newlines(self):
        """Test handling newlines."""
        message = "Line 1\n\n\nLine 2\nLine 3"
        result = sanitize_message(message)
        assert "  " not in result
    
    def test_truncate_long_message(self):
        """Test truncating long messages."""
        message = "a" * 1000
        result = sanitize_message(message, max_length=100)
        assert len(result) == 100
        assert result.endswith("...")
    
    def test_no_truncate_short_message(self):
        """Test not truncating short messages."""
        message = "Short message"
        result = sanitize_message(message, max_length=100)
        assert result == message


class TestCoordinateFormatting:
    """Tests for coordinate formatting."""
    
    def test_format_north_east(self):
        """Test formatting coordinates in NE quadrant."""
        result = format_coordinates(37.7749, -122.4194)
        assert "N" in result
        assert "W" in result
        assert "37.7749" in result
    
    def test_format_south_west(self):
        """Test formatting coordinates in SW quadrant."""
        result = format_coordinates(-33.8688, 151.2093)
        assert "S" in result
        assert "E" in result
    
    def test_format_zero_coordinates(self):
        """Test formatting zero coordinates."""
        result = format_coordinates(0, 0)
        assert "0.0000°N" in result
        assert "0.0000°E" in result


class TestLogger:
    """Tests for logger setup."""
    
    def test_logger_creation(self):
        """Test creating a logger."""
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
    
    def test_logger_with_custom_level(self):
        """Test creating logger with custom level."""
        logger = setup_logger("test_debug", level=logging.DEBUG)
        assert logger.level == logging.DEBUG
