import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

// Alert severity colors
const severityColors = {
  critical: '#d32f2f',
  high: '#f57c00',
  medium: '#fbc02d',
  low: '#388e3c',
  info: '#1976d2',
};

// Alert type icons mapping
const alertTypeIcons = {
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
  };
  source: string;
  created_at: string;
  expires_at?: string;
  target_languages: string[];
  metadata?: Record<string, any>;
}

interface AlertCardProps {
  alert: Alert;
  onEdit?: (alert: Alert) => void;
  onDelete?: (alertId: string) => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({ alert, onEdit, onDelete }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <ErrorIcon sx={{ color: severityColors[severity as keyof typeof severityColors] }} />;
      case 'medium':
        return <WarningIcon sx={{ color: severityColors[severity as keyof typeof severityColors] }} />;
      default:
        return <CheckCircleIcon sx={{ color: severityColors[severity as keyof typeof severityColors] }} />;
    }
  };

  return (
    <Card sx={{ mb: 2, borderLeft: `4px solid ${severityColors[alert.severity as keyof typeof severityColors]}` }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <Typography variant="h4" component="span">
              {alertTypeIcons[alert.alert_type as keyof typeof alertTypeIcons]}
            </Typography>
            {getSeverityIcon(alert.severity)}
            <Typography variant="h6" component="h3">
              {alert.title}
            </Typography>
          </Box>
          <Box>
            {onEdit && (
              <IconButton size="small" onClick={() => onEdit(alert)} color="primary">
                <EditIcon />
              </IconButton>
            )}
            {onDelete && (
              <IconButton size="small" onClick={() => onDelete(alert.alert_id)} color="error">
                <DeleteIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        <Typography variant="body1" color="text.secondary" paragraph>
          {alert.message}
        </Typography>

        <Grid container spacing={1} mb={2}>
          <Grid item>
            <Chip
              label={alert.severity.toUpperCase()}
              size="small"
              sx={{
                backgroundColor: severityColors[alert.severity as keyof typeof severityColors],
                color: 'white',
              }}
            />
          </Grid>
          <Grid item>
            <Chip label={alert.alert_type.toUpperCase()} size="small" variant="outlined" />
          </Grid>
          <Grid item>
            <Chip label={`Source: ${alert.source}`} size="small" variant="outlined" />
          </Grid>
        </Grid>

        {alert.location && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            📍 Location: {alert.location.city && `${alert.location.city}, `}
            {alert.location.region && `${alert.location.region}, `}
            {alert.location.country}
            {alert.location.latitude && ` (${alert.location.latitude.toFixed(4)}°, ${alert.location.longitude.toFixed(4)}°)`}
          </Typography>
        )}

        <Box display="flex" gap={1} mt={1}>
          <Typography variant="caption" color="text.secondary">
            Created: {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}
          </Typography>
          {alert.expires_at && (
            <Typography variant="caption" color="text.secondary">
              • Expires: {format(new Date(alert.expires_at), 'MMM dd, yyyy HH:mm')}
            </Typography>
          )}
        </Box>

        {alert.target_languages && alert.target_languages.length > 0 && (
          <Box mt={1}>
            <Typography variant="caption" color="text.secondary">
              Languages: {alert.target_languages.join(', ').toUpperCase()}
            </Typography>
          </Box>
        )}

        {alert.metadata && Object.keys(alert.metadata).length > 0 && (
          <Box mt={1}>
            <Typography variant="caption" color="text.secondary">
              Metadata: {JSON.stringify(alert.metadata)}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

interface AlertListProps {
  apiUrl: string;
  refreshInterval?: number;
}

export const AlertList: React.FC<AlertListProps> = ({ apiUrl, refreshInterval = 30000 }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/v1/alerts`);
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setAlerts(data.alerts || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, refreshInterval);
    return () => clearInterval(interval);
  }, [apiUrl, refreshInterval]);

  const handleDelete = async (alertId: string) => {
    if (!confirm('Are you sure you want to delete this alert?')) return;
    
    try {
      await fetch(`${apiUrl}/api/v1/alerts/${alertId}`, { method: 'DELETE' });
      setAlerts(alerts.filter(a => a.alert_id !== alertId));
    } catch (err) {
      alert('Failed to delete alert');
    }
  };

  if (loading && alerts.length === 0) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h2">
          Active Alerts
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchAlerts}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {alerts.length === 0 ? (
        <Alert severity="info">No active alerts at this time.</Alert>
      ) : (
        alerts.map(alert => (
          <AlertCard
            key={alert.alert_id}
            alert={alert}
            onDelete={handleDelete}
          />
        ))
      )}
    </Box>
  );
};

export default AlertList;
