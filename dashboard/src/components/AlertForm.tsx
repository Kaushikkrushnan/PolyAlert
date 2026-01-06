import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  MenuItem,
  Grid,
  Typography,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Send as SendIcon, Add as AddIcon } from '@mui/icons-material';

const ALERT_TYPES = [
  { value: 'earthquake', label: '🌍 Earthquake', emoji: '🌍' },
  { value: 'flood', label: '🌊 Flood', emoji: '🌊' },
  { value: 'fire', label: '🔥 Fire', emoji: '🔥' },
  { value: 'storm', label: '⛈️ Storm', emoji: '⛈️' },
  { value: 'tsunami', label: '🌊 Tsunami', emoji: '🌊' },
  { value: 'tornado', label: '🌪️ Tornado', emoji: '🌪️' },
  { value: 'hurricane', label: '🌀 Hurricane', emoji: '🌀' },
  { value: 'landslide', label: '🏔️ Landslide', emoji: '🏔️' },
  { value: 'volcano', label: '🌋 Volcano', emoji: '🌋' },
  { value: 'other', label: 'ℹ️ Other', emoji: 'ℹ️' },
];

const SEVERITY_LEVELS = [
  { value: 'critical', label: 'Critical', color: '#d32f2f' },
  { value: 'high', label: 'High', color: '#f57c00' },
  { value: 'medium', label: 'Medium', color: '#fbc02d' },
  { value: 'low', label: 'Low', color: '#388e3c' },
  { value: 'info', label: 'Info', color: '#1976d2' },
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'zh', label: 'Chinese' },
  { value: 'hi', label: 'Hindi' },
  { value: 'ar', label: 'Arabic' },
  { value: 'fr', label: 'French' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'ja', label: 'Japanese' },
];

interface AlertFormData {
  title: string;
  message: string;
  alert_type: string;
  severity: string;
  source: string;
  latitude: string;
  longitude: string;
  city: string;
  region: string;
  country: string;
  target_languages: string[];
}

interface AlertFormProps {
  apiUrl: string;
  onSuccess?: (response: any) => void;
}

export const AlertForm: React.FC<AlertFormProps> = ({ apiUrl, onSuccess }) => {
  const [formData, setFormData] = useState<AlertFormData>({
    title: '',
    message: '',
    alert_type: 'earthquake',
    severity: 'medium',
    source: 'Manual',
    latitude: '',
    longitude: '',
    city: '',
    region: '',
    country: '',
    target_languages: ['en'],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleChange = (field: keyof AlertFormData) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleLanguageToggle = (language: string) => {
    setFormData(prev => ({
      ...prev,
      target_languages: prev.target_languages.includes(language)
        ? prev.target_languages.filter(l => l !== language)
        : [...prev.target_languages, language],
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const payload: any = {
        title: formData.title,
        message: formData.message,
        alert_type: formData.alert_type,
        severity: formData.severity,
        source: formData.source,
        target_languages: formData.target_languages,
      };

      // Add location if provided
      if (formData.latitude && formData.longitude) {
        payload.location = {
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude),
        };
        if (formData.city) payload.location.city = formData.city;
        if (formData.region) payload.location.region = formData.region;
        if (formData.country) payload.location.country = formData.country;
      }

      const response = await fetch(`${apiUrl}/api/v1/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to send alert');
      }

      const data = await response.json();
      setSuccess(`Alert sent successfully! Alert ID: ${data.alert_id}`);
      
      // Reset form
      setFormData({
        title: '',
        message: '',
        alert_type: 'earthquake',
        severity: 'medium',
        source: 'Manual',
        latitude: '',
        longitude: '',
        city: '',
        region: '',
        country: '',
        target_languages: ['en'],
      });

      if (onSuccess) onSuccess(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2" gutterBottom>
          Create New Alert
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Alert Title"
                value={formData.title}
                onChange={handleChange('title')}
                required
                placeholder="e.g., Earthquake Alert - San Francisco"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Alert Message"
                value={formData.message}
                onChange={handleChange('message')}
                required
                multiline
                rows={4}
                placeholder="Detailed description of the alert..."
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Alert Type"
                value={formData.alert_type}
                onChange={handleChange('alert_type')}
                required
              >
                {ALERT_TYPES.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Severity"
                value={formData.severity}
                onChange={handleChange('severity')}
                required
              >
                {SEVERITY_LEVELS.map(level => (
                  <MenuItem key={level.value} value={level.value}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: level.color,
                        }}
                      />
                      {level.label}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Location Information */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Location (Optional)
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Latitude"
                type="number"
                value={formData.latitude}
                onChange={handleChange('latitude')}
                placeholder="e.g., 37.7749"
                inputProps={{ step: '0.0001' }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Longitude"
                type="number"
                value={formData.longitude}
                onChange={handleChange('longitude')}
                placeholder="e.g., -122.4194"
                inputProps={{ step: '0.0001' }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="City"
                value={formData.city}
                onChange={handleChange('city')}
                placeholder="e.g., San Francisco"
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Region/State"
                value={formData.region}
                onChange={handleChange('region')}
                placeholder="e.g., California"
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Country"
                value={formData.country}
                onChange={handleChange('country')}
                placeholder="e.g., USA"
              />
            </Grid>

            {/* Additional Settings */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Source"
                value={formData.source}
                onChange={handleChange('source')}
                placeholder="e.g., USGS, Manual"
              />
            </Grid>

            {/* Target Languages */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Target Languages
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {LANGUAGES.map(lang => (
                  <Chip
                    key={lang.value}
                    label={lang.label}
                    onClick={() => handleLanguageToggle(lang.value)}
                    color={formData.target_languages.includes(lang.value) ? 'primary' : 'default'}
                    variant={formData.target_languages.includes(lang.value) ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </Grid>

            {/* Alerts */}
            {error && (
              <Grid item xs={12}>
                <Alert severity="error">{error}</Alert>
              </Grid>
            )}

            {success && (
              <Grid item xs={12}>
                <Alert severity="success">{success}</Alert>
              </Grid>
            )}

            {/* Submit Button */}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                disabled={loading}
              >
                {loading ? 'Sending Alert...' : 'Send Alert'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </CardContent>
    </Card>
  );
};

export default AlertForm;
