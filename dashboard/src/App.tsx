import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning as AlertIcon,
  AddCircle as AddIcon,
  Map as MapIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import AlertList from './components/AlertList';
import AlertForm from './components/AlertForm';
import AlertMap from './components/AlertMap';

const drawerWidth = 240;

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Configuration - Replace with your actual values
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Alerts', icon: <AlertIcon />, path: '/alerts' },
  { text: 'Create Alert', icon: <AddIcon />, path: '/create' },
  { text: 'Map View', icon: <MapIcon />, path: '/map' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* App Bar */}
          <AppBar
            position="fixed"
            sx={{
              zIndex: theme => theme.zIndex.drawer + 1,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            <Toolbar>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                🚨 PolyAlert Dashboard
              </Typography>
              <Typography variant="body2">
                Open-Source Disaster Alert System
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Sidebar */}
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto', mt: 2 }}>
              <List>
                {menuItems.map(item => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton component={Link} to={item.path}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>

          {/* Main Content */}
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard apiUrl={API_URL} />} />
                <Route path="/alerts" element={<AlertList apiUrl={API_URL} />} />
                <Route
                  path="/create"
                  element={
                    <AlertForm
                      apiUrl={API_URL}
                      onSuccess={data => {
                        console.log('Alert created:', data);
                      }}
                    />
                  }
                />
                <Route
                  path="/map"
                  element={
                    <AlertMap
                      alerts={[]} // This should fetch alerts from API
                      googleMapsApiKey={GOOGLE_MAPS_API_KEY}
                    />
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <Box>
                      <Typography variant="h4">Settings</Typography>
                      <Typography variant="body1" mt={2}>
                        Configuration options coming soon...
                      </Typography>
                    </Box>
                  }
                />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
