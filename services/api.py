"""Cloud Run API for alert ingestion."""
import json
import logging
import os
from flask import Flask, request, jsonify
from typing import Dict

from services.ingestion import IngestionService
from core.config import Config
from core.utils import setup_logger


logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize ingestion service
ingestion_service = IngestionService()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "polyalert-ingestion",
        "version": "0.1.0"
    }), 200


@app.route("/api/v1/alerts", methods=["POST"])
def ingest_alert():
    """Ingest a new disaster alert.
    
    Expected JSON payload:
    {
        "title": "Earthquake Alert",
        "message": "A 7.2 magnitude earthquake detected...",
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
        "target_languages": ["en", "es", "zh", "hi"]
    }
    """
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        # Ingest alert
        result = ingestion_service.ingest_alert(data)
        
        return jsonify(result), 201
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Internal error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@app.route("/api/v1/alerts/batch", methods=["POST"])
def ingest_alerts_batch():
    """Ingest multiple alerts in batch.
    
    Expected JSON payload:
    {
        "alerts": [
            {...alert1...},
            {...alert2...}
        ]
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        alerts = data.get("alerts", [])
        
        if not alerts or not isinstance(alerts, list):
            return jsonify({
                "status": "error",
                "message": "Request must contain 'alerts' array"
            }), 400
        
        if len(alerts) > 100:
            return jsonify({
                "status": "error",
                "message": "Maximum 100 alerts per batch"
            }), 400
        
        # Process each alert
        results = []
        errors = []
        
        for idx, alert_data in enumerate(alerts):
            try:
                result = ingestion_service.ingest_alert(alert_data)
                results.append(result)
            except Exception as e:
                errors.append({
                    "index": idx,
                    "error": str(e)
                })
        
        response = {
            "status": "partial_success" if errors else "success",
            "processed": len(results),
            "failed": len(errors),
            "results": results,
        }
        
        if errors:
            response["errors"] = errors
        
        return jsonify(response), 201 if not errors else 207
        
    except Exception as e:
        logger.error(f"Batch ingestion error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors."""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405


if __name__ == "__main__":
    port = Config.API_PORT
    host = Config.API_HOST
    debug = Config.DEBUG
    
    logger.info(f"Starting PolyAlert Ingestion API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
