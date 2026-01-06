# PolyAlert 🚨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**PolyAlert** is an open-source, serverless disaster alert system built on Google Cloud Platform. It uses AI-powered translation to automatically convert disaster warnings into regional languages and broadcasts them via SMS, WhatsApp, and Voice calls. The system features real-time monitoring through a Firebase Admin Dashboard and is secured with Cloud Armor.

## 🌟 Features

- **Multi-Channel Delivery**: Send alerts via SMS, WhatsApp, and Voice calls
- **AI-Powered Translation**: Automatic translation using Google Cloud Translation API
- **Real-Time Monitoring**: Firebase-hosted admin dashboard with Google Maps integration
- **Scalable Architecture**: Serverless design using Cloud Run, Pub/Sub, and Cloud Functions
- **Flexible Alert Types**: Support for earthquakes, floods, fires, storms, tsunamis, and more
- **Batch Processing**: Ingest multiple alerts simultaneously
- **Comprehensive Testing**: Full unit and integration test coverage

## 🏗️ Architecture

```
┌─────────────┐
│   Sources   │ (USGS, Weather APIs, Manual)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Ingestion API    │ (Cloud Run)
│ - Validation     │
│ - Pub/Sub Publish│
└────────┬─────────┘
         │
         ▼
   ┌────────────┐
   │  Pub/Sub   │ (alert-ingestion)
   └─────┬──────┘
         │
    ┌────┴────────────┐
    │                 │
    ▼                 ▼
┌──────────┐   ┌──────────────┐
│Translation│   │   Routing    │
│ Service  │   │   Service    │
└─────┬────┘   └──────┬───────┘
      │                │
      ▼                ▼
┌────────────────────────────┐
│    Delivery Adapters       │
│  - SMS (Twilio)            │
│  - WhatsApp                │
│  - Voice Calls             │
└────────────┬───────────────┘
             │
             ▼
      ┌──────────────┐
      │  Firestore   │ (Alert Storage)
      └──────────────┘
```

## 📁 Project Structure

```
PolyAlert/
├── core/                  # Core data models and utilities
│   ├── __init__.py
│   ├── models.py         # Alert, Translation, Delivery models
│   ├── config.py         # Configuration management
│   └── utils.py          # Utility functions
├── services/             # Microservices
│   ├── __init__.py
│   ├── ingestion.py      # Alert ingestion service
│   └── api.py            # Cloud Run API endpoints
├── adapters/             # External service adapters
│   └── (SMS, WhatsApp, Voice adapters)
├── dashboard/            # Admin dashboard (Firebase)
│   └── (React/Vue frontend)
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   │   ├── test_models.py
│   │   ├── test_utils.py
│   │   ├── test_ingestion.py
│   │   └── test_api.py
│   └── integration/     # Integration tests
│       └── test_ingestion_flow.py
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml       # Project configuration
├── Dockerfile           # Cloud Run container
├── API.md              # API documentation
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Cloud Project with enabled APIs:
  - Cloud Run
  - Pub/Sub
  - Firestore
  - Cloud Translation API
  - Firebase Hosting

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kaushikkrushnan/PolyAlert.git
   cd PolyAlert
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export GCP_PROJECT_ID=your-project-id
   export GCP_REGION=us-central1
   export PUBSUB_ALERT_TOPIC=alert-ingestion
   export ENV=development
   ```

4. **Run the ingestion API locally**
   ```bash
   python services/api.py
   ```

The API will be available at `http://localhost:8080`

## 📝 Usage

### Ingest a Single Alert

```bash
curl -X POST http://localhost:8080/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Earthquake Alert",
    "message": "A 7.2 magnitude earthquake detected near San Francisco",
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
  }'
```

### Ingest Multiple Alerts (Batch)

```bash
curl -X POST http://localhost:8080/api/v1/alerts/batch \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [
      {
        "title": "Flood Warning",
        "message": "Flash flood warning in effect",
        "alert_type": "flood",
        "severity": "high"
      },
      {
        "title": "Storm Alert",
        "message": "Severe thunderstorm approaching",
        "alert_type": "storm",
        "severity": "medium"
      }
    ]
  }'
```

See [API.md](API.md) for complete API documentation.

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Generate Coverage Report
```bash
pytest --cov=core --cov=services --cov-report=html
open htmlcov/index.html
```

### Run Linter
```bash
black .
flake8 .
isort .
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t polyalert-ingestion .
```

### Run Container Locally
```bash
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e PUBSUB_ALERT_TOPIC=alert-ingestion \
  polyalert-ingestion
```

## ☁️ Google Cloud Deployment

### Deploy to Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/polyalert-ingestion

# Deploy to Cloud Run
gcloud run deploy polyalert-ingestion \
  --image gcr.io/PROJECT_ID/polyalert-ingestion \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=PROJECT_ID,PUBSUB_ALERT_TOPIC=alert-ingestion
```

### Create Pub/Sub Topic
```bash
gcloud pubsub topics create alert-ingestion
gcloud pubsub topics create alert-translation
gcloud pubsub topics create alert-delivery
```

### Set up Firestore
```bash
gcloud firestore databases create --location=us-central
```

## 📊 Data Models

### Alert Types
- `earthquake` - Seismic activity alerts
- `flood` - Flooding warnings
- `fire` - Wildfire alerts
- `storm` - Storm and weather warnings
- `tsunami` - Tsunami warnings
- `tornado` - Tornado alerts
- `hurricane` - Hurricane warnings
- `landslide` - Landslide warnings
- `volcano` - Volcanic activity alerts
- `other` - General disaster alerts

### Severity Levels
- `critical` - Immediate action required (48h expiry)
- `high` - Urgent attention needed (24h expiry)
- `medium` - Moderate concern (24h expiry)
- `low` - Minor concern (24h expiry)
- `info` - Informational only (12h expiry)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Cloud Platform for serverless infrastructure
- Cloud Translation API for multilingual support
- Twilio for SMS/Voice delivery capabilities
- Firebase for hosting and real-time features

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for disaster preparedness and community safety**
