# PolyAlert API Documentation

## Overview
PolyAlert is an open-source disaster alert system built on Google Cloud Platform. It provides APIs for ingesting disaster alerts and distributing them via multiple channels (SMS, WhatsApp, Voice).

## Architecture

### Components
- **Ingestion Service** (Cloud Run): REST API for receiving disaster alerts
- **Pub/Sub**: Message queue for alert distribution
- **Translation Service**: Auto-translate alerts using Cloud Translation API
- **Delivery Adapters**: SMS, WhatsApp, and Voice delivery
- **Firestore**: Alert storage and tracking
- **Admin Dashboard**: Firebase-hosted UI for monitoring

### Data Flow
1. Alert submitted to Ingestion API
2. Validated and published to Pub/Sub
3. Translation Service subscribes and translates to target languages
4. Routing Service determines recipients and channels
5. Delivery Adapters send notifications
6. Status tracked in Firestore

## API Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "polyalert-ingestion",
  "version": "0.1.0"
}
```

### Ingest Alert
```
POST /api/v1/alerts
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Earthquake Alert",
  "message": "A 7.2 magnitude earthquake detected near San Francisco",
  "alert_type": "earthquake",
  "severity": "critical",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "city": "San Francisco",
    "region": "California",
    "country": "USA",
    "radius_km": 50
  },
  "source": "USGS",
  "source_language": "en",
  "target_languages": ["en", "es", "zh", "hi"],
  "metadata": {
    "magnitude": 7.2,
    "depth_km": 10
  }
}
```

**Required Fields:**
- `title` (string): Alert title
- `message` (string): Alert message (max 5000 chars)
- `alert_type` (string): Type of alert
- `severity` (string): Severity level

**Alert Types:**
- `earthquake`
- `flood`
- `fire`
- `storm`
- `tsunami`
- `tornado`
- `hurricane`
- `landslide`
- `volcano`
- `other`

**Severity Levels:**
- `critical`
- `high`
- `medium`
- `low`
- `info`

**Response (201 Created):**
```json
{
  "status": "success",
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "1234567890",
  "created_at": "2024-01-01T12:00:00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Missing required field: title"
}
```

### Batch Ingest Alerts
```
POST /api/v1/alerts/batch
Content-Type: application/json
```

**Request Body:**
```json
{
  "alerts": [
    {
      "title": "Alert 1",
      "message": "First alert",
      "alert_type": "earthquake",
      "severity": "high"
    },
    {
      "title": "Alert 2",
      "message": "Second alert",
      "alert_type": "flood",
      "severity": "medium"
    }
  ]
}
```

**Limits:**
- Maximum 100 alerts per batch

**Response (201 Created):**
```json
{
  "status": "success",
  "processed": 2,
  "failed": 0,
  "results": [
    {
      "status": "success",
      "alert_id": "...",
      "message_id": "..."
    },
    {
      "status": "success",
      "alert_id": "...",
      "message_id": "..."
    }
  ]
}
```

**Partial Success Response (207 Multi-Status):**
```json
{
  "status": "partial_success",
  "processed": 1,
  "failed": 1,
  "results": [...],
  "errors": [
    {
      "index": 1,
      "error": "Invalid alert_type"
    }
  ]
}
```

## Development

### Setup
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=core --cov=services --cov-report=html

# Run linter
black .
flake8 .
```

### Run Locally
```bash
# Set environment variables
export GCP_PROJECT_ID=your-project-id
export PUBSUB_ALERT_TOPIC=alert-ingestion
export ENV=development

# Run the API
python services/api.py
```

### Docker
```bash
# Build image
docker build -t polyalert-ingestion .

# Run container
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e PUBSUB_ALERT_TOPIC=alert-ingestion \
  polyalert-ingestion
```

## Deployment

### Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/polyalert-ingestion
gcloud run deploy polyalert-ingestion \
  --image gcr.io/PROJECT_ID/polyalert-ingestion \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Environment Variables
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCP_REGION`: Google Cloud Region (default: us-central1)
- `PUBSUB_ALERT_TOPIC`: Pub/Sub topic for alerts
- `ENV`: Environment (development/production)
- `DEBUG`: Enable debug mode (true/false)

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Test Coverage
```bash
pytest --cov=core --cov=services --cov-report=html
open htmlcov/index.html
```

## Contributing
Please ensure all tests pass and code is formatted with Black before submitting pull requests.

## License
MIT License
