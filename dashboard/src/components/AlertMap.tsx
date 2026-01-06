import React, { useState, useCallback } from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow, Circle } from '@react-google-maps/api';
import { Box, Card, CardContent, Typography, Chip } from '@mui/material';

const mapContainerStyle = {
  width: '100%',
  height: '600px',
};

const defaultCenter = {
  lat: 37.7749,
  lng: -122.4194,
};

interface Alert {
  alert_id: string;
  title: string;
  message: string;
  alert_type: string;
  severity: string;
  location?: {
    latitude: number;
    longitude: number;
    city?: string;
    region?: string;
    country?: string;
    radius_km?: number;
  };
  created_at: string;
}

interface AlertMapProps {
  alerts: Alert[];
  googleMapsApiKey: string;
  center?: { lat: number; lng: number };
  zoom?: number;
}

const severityColors: Record<string, string> = {
  critical: '#d32f2f',
  high: '#f57c00',
  medium: '#fbc02d',
  low: '#388e3c',
  info: '#1976d2',
};

const alertTypeIcons: Record<string, string> = {
  earthquake: '🌍',
  flood: '🌊',
  fire: '🔥',
  storm: '⛈️',
  tsunami: '🌊',
  tornado: '🌪️',
  hurricane: '🌀',
  landslide: '🏔️',
  volcano: '🌋',
  other: 'ℹ️',
};

export const AlertMap: React.FC<AlertMapProps> = ({
  alerts,
  googleMapsApiKey,
  center = defaultCenter,
  zoom = 10,
}) => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [mapCenter, setMapCenter] = useState(center);

  const onMapLoad = useCallback((map: google.maps.Map) => {
    // Fit bounds to show all markers
    if (alerts.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      alerts.forEach(alert => {
        if (alert.location) {
          bounds.extend({
            lat: alert.location.latitude,
            lng: alert.location.longitude,
          });
        }
      });
      map.fitBounds(bounds);
    }
  }, [alerts]);

  const getMarkerIcon = (alert: Alert) => {
    return {
      path: google.maps.SymbolPath.CIRCLE,
      fillColor: severityColors[alert.severity] || '#1976d2',
      fillOpacity: 0.8,
      strokeColor: '#ffffff',
      strokeWeight: 2,
      scale: alert.severity === 'critical' ? 12 : alert.severity === 'high' ? 10 : 8,
    };
  };

  return (
    <Card>
      <CardContent>
        <Box mb={2}>
          <Typography variant="h5" component="h2" gutterBottom>
            Alert Map
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Showing {alerts.filter(a => a.location).length} alerts with location data
          </Typography>
        </Box>

        <LoadScript googleMapsApiKey={googleMapsApiKey}>
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={mapCenter}
            zoom={zoom}
            onLoad={onMapLoad}
            options={{
              streetViewControl: false,
              mapTypeControl: true,
              fullscreenControl: true,
            }}
          >
            {alerts.map(alert => {
              if (!alert.location) return null;

              const position = {
                lat: alert.location.latitude,
                lng: alert.location.longitude,
              };

              return (
                <React.Fragment key={alert.alert_id}>
                  <Marker
                    position={position}
                    onClick={() => setSelectedAlert(alert)}
                    icon={getMarkerIcon(alert)}
                    title={alert.title}
                  />

                  {/* Show affected radius if available */}
                  {alert.location.radius_km && (
                    <Circle
                      center={position}
                      radius={alert.location.radius_km * 1000} // Convert km to meters
                      options={{
                        fillColor: severityColors[alert.severity],
                        fillOpacity: 0.15,
                        strokeColor: severityColors[alert.severity],
                        strokeOpacity: 0.4,
                        strokeWeight: 1,
                      }}
                    />
                  )}

                  {selectedAlert?.alert_id === alert.alert_id && (
                    <InfoWindow
                      position={position}
                      onCloseClick={() => setSelectedAlert(null)}
                    >
                      <Box sx={{ maxWidth: 300 }}>
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Typography variant="h6" component="div">
                            {alertTypeIcons[alert.alert_type]} {alert.title}
                          </Typography>
                        </Box>
                        
                        <Typography variant="body2" paragraph>
                          {alert.message}
                        </Typography>

                        <Box display="flex" gap={1} mb={1}>
                          <Chip
                            label={alert.severity.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: severityColors[alert.severity],
                              color: 'white',
                            }}
                          />
                          <Chip
                            label={alert.alert_type.toUpperCase()}
                            size="small"
                            variant="outlined"
                          />
                        </Box>

                        {alert.location && (
                          <Typography variant="caption" color="text.secondary">
                            📍 {alert.location.city && `${alert.location.city}, `}
                            {alert.location.region && `${alert.location.region}, `}
                            {alert.location.country}
                            <br />
                            {alert.location.latitude.toFixed(4)}°,{' '}
                            {alert.location.longitude.toFixed(4)}°
                            {alert.location.radius_km && ` • Radius: ${alert.location.radius_km} km`}
                          </Typography>
                        )}

                        <Typography variant="caption" display="block" mt={1} color="text.secondary">
                          {new Date(alert.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                    </InfoWindow>
                  )}
                </React.Fragment>
              );
            })}
          </GoogleMap>
        </LoadScript>

        {/* Legend */}
        <Box mt={2} display="flex" flexWrap="wrap" gap={2}>
          {Object.entries(severityColors).map(([severity, color]) => (
            <Box key={severity} display="flex" alignItems="center" gap={1}>
              <Box
                sx={{
                  width: 16,
                  height: 16,
                  borderRadius: '50%',
                  backgroundColor: color,
                  border: '2px solid white',
                }}
              />
              <Typography variant="caption" textTransform="capitalize">
                {severity}
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlertMap;
