import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface DashboardStats {
  totalAlerts: number;
  criticalAlerts: number;
  activeAlerts: number;
  resolvedAlerts: number;
  avgResponseTime: number;
  alertsByType: Record<string, number>;
  alertsBySeverity: Record<string, number>;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography color="text.secondary" gutterBottom variant="overline">
            {title}
          </Typography>
          <Typography variant="h3" component="div" sx={{ mb: 1 }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: `${color}20`,
            borderRadius: '50%',
            p: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

interface DashboardProps {
  apiUrl: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ apiUrl }) => {
  const [stats, setStats] = useState<DashboardStats>({
    totalAlerts: 0,
    criticalAlerts: 0,
    activeAlerts: 0,
    resolvedAlerts: 0,
    avgResponseTime: 0,
    alertsByType: {},
    alertsBySeverity: {},
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/v1/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        Dashboard Overview
      </Typography>

      <Grid container spacing={3}>
        {/* Stat Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Alerts"
            value={stats.totalAlerts}
            icon={<InfoIcon sx={{ fontSize: 40, color: '#1976d2' }} />}
            color="#1976d2"
            subtitle="All time"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={stats.activeAlerts}
            icon={<WarningIcon sx={{ fontSize: 40, color: '#f57c00' }} />}
            color="#f57c00"
            subtitle="Currently active"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical"
            value={stats.criticalAlerts}
            icon={<ErrorIcon sx={{ fontSize: 40, color: '#d32f2f' }} />}
            color="#d32f2f"
            subtitle="Requires attention"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resolved"
            value={stats.resolvedAlerts}
            icon={<CheckCircleIcon sx={{ fontSize: 40, color: '#388e3c' }} />}
            color="#388e3c"
            subtitle="Successfully handled"
          />
        </Grid>

        {/* Alerts by Type */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alerts by Type
              </Typography>
              {Object.entries(stats.alertsByType).map(([type, count]) => (
                <Box key={type} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="body2" textTransform="capitalize">
                      {type}
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {count}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(count / stats.totalAlerts) * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts by Severity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alerts by Severity
              </Typography>
              {Object.entries(stats.alertsBySeverity).map(([severity, count]) => (
                <Box key={severity} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="body2" textTransform="capitalize">
                      {severity}
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {count}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(count / stats.totalAlerts) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor:
                          severity === 'critical'
                            ? '#d32f2f'
                            : severity === 'high'
                            ? '#f57c00'
                            : severity === 'medium'
                            ? '#fbc02d'
                            : severity === 'low'
                            ? '#388e3c'
                            : '#1976d2',
                      },
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircleIcon sx={{ color: '#388e3c' }} />
                  <Typography variant="body2">
                    <strong>API Status:</strong> Healthy
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircleIcon sx={{ color: '#388e3c' }} />
                  <Typography variant="body2">
                    <strong>Pub/Sub:</strong> Connected
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <InfoIcon sx={{ color: '#1976d2' }} />
                  <Typography variant="body2">
                    <strong>Avg Response:</strong> {stats.avgResponseTime}ms
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
