# PolyAlert Frontend Snippets

Complete React + TypeScript frontend implementation for the PolyAlert admin dashboard.

## 📦 What's Included

### Core Components (4 files)

1. **AlertList.tsx** - Display and manage alerts
   - Real-time auto-refresh
   - Severity color coding
   - Alert type icons
   - Location display
   - Edit/Delete actions

2. **AlertForm.tsx** - Create new alerts
   - 10 alert types with emojis
   - 5 severity levels
   - Location inputs (coordinates + address)
   - Multi-language selection
   - Form validation

3. **Dashboard.tsx** - Statistics overview
   - Total/Active/Critical/Resolved counters
   - Alerts by type chart
   - Alerts by severity chart
   - System status indicators

4. **AlertMap.tsx** - Interactive Google Maps
   - Pin markers color-coded by severity
   - Info windows with alert details
   - Affected radius visualization
   - Auto-fit bounds

### Application Files

5. **App.tsx** - Main application with routing
   - Material-UI theme
   - Sidebar navigation
   - Multiple routes (Dashboard, Alerts, Create, Map)

6. **index.tsx** - Entry point

### Configuration

7. **package.json** - Dependencies and scripts
8. **tsconfig.json** - TypeScript configuration
9. **vite.config.ts** - Vite build configuration
10. **README.md** - Dashboard documentation

### Styling

11. **index.css** - Global styles

## 🚀 Quick Start

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8080
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
EOF

# Start development server
npm run dev

# Build for production
npm run build
```

## 📸 Screenshots

The dashboard includes:

- **Dashboard Page**: Statistics cards, charts, system status
- **Alerts Page**: List of all alerts with filters
- **Create Alert Page**: Form with all fields
- **Map View**: Interactive Google Maps with markers

## 🎨 Features

### Dashboard Component
- ✅ 4 stat cards (Total, Active, Critical, Resolved)
- ✅ Alerts by Type chart with progress bars
- ✅ Alerts by Severity chart with color coding
- ✅ System health indicators

### Alert List Component
- ✅ Auto-refresh every 30 seconds
- ✅ Severity badges (Critical, High, Medium, Low, Info)
- ✅ Alert type icons (🌍 🌊 🔥 ⛈️ etc.)
- ✅ Location display with coordinates
- ✅ Edit and Delete actions
- ✅ Loading states and error handling

### Alert Form Component
- ✅ 10 alert types with emoji selectors
- ✅ 5 severity levels with color indicators
- ✅ Location fields (lat/lng, city, region, country)
- ✅ Multi-language selection with chips
- ✅ Source field
- ✅ Form validation
- ✅ Success/Error messages

### Alert Map Component
- ✅ Google Maps integration
- ✅ Color-coded markers by severity
- ✅ Click markers to view alert details
- ✅ Affected radius circles
- ✅ Auto-fit bounds to show all alerts
- ✅ Legend for severity colors

## 🔧 API Integration

All components connect to the backend API:

```typescript
// Fetch alerts
GET ${API_URL}/api/v1/alerts

// Create alert
POST ${API_URL}/api/v1/alerts
Body: {
  title, message, alert_type, severity,
  location: { latitude, longitude, city },
  target_languages: ["en", "es"]
}

// Fetch statistics
GET ${API_URL}/api/v1/stats
```

## 🎨 Customization

### Change Theme Colors

Edit `src/App.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' }, // Change this
    secondary: { main: '#764ba2' }, // And this
  },
});
```

### Add New Alert Type

Edit `src/components/AlertForm.tsx`:

```typescript
const ALERT_TYPES = [
  // Add your custom type
  { value: 'avalanche', label: '🏔️ Avalanche', emoji: '🏔️' },
  // ... existing types
];
```

### Modify Severity Colors

Edit severity colors in any component:

```typescript
const severityColors = {
  critical: '#d32f2f', // Red
  high: '#f57c00',     // Orange
  medium: '#fbc02d',   // Yellow
  low: '#388e3c',      // Green
  info: '#1976d2',     // Blue
};
```

## 📦 Dependencies

```json
{
  "react": "^18.2.0",
  "@mui/material": "^5.14.0",
  "@mui/icons-material": "^5.14.0",
  "react-router-dom": "^6.20.0",
  "@react-google-maps/api": "^2.19.0",
  "axios": "^1.6.0",
  "recharts": "^2.10.0",
  "date-fns": "^2.30.0"
}
```

## 🚀 Deployment Options

### Option 1: Firebase Hosting

```bash
npm run build
firebase init hosting
firebase deploy
```

### Option 2: Docker

```bash
docker build -t polyalert-dashboard .
docker run -p 80:80 polyalert-dashboard
```

### Option 3: Netlify

```bash
npm run build
# Upload build/ directory to Netlify
```

## 📱 Responsive Design

All components are fully responsive:
- Desktop: Full sidebar navigation
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation bar

## 🔐 Environment Variables

Create `.env` file:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8080

# Google Maps API Key (required for map)
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...

# Optional: Enable debug mode
REACT_APP_DEBUG=true
```

## 🧪 Testing

```bash
# Run linter
npm run lint

# Format code
npm run format

# Type check
npx tsc --noEmit
```

## 📚 Component Usage Examples

### Using AlertList

```tsx
import AlertList from './components/AlertList';

<AlertList 
  apiUrl="http://localhost:8080"
  refreshInterval={30000}
/>
```

### Using AlertForm

```tsx
import AlertForm from './components/AlertForm';

<AlertForm 
  apiUrl="http://localhost:8080"
  onSuccess={(data) => console.log('Alert created:', data)}
/>
```

### Using AlertMap

```tsx
import AlertMap from './components/AlertMap';

<AlertMap 
  alerts={alertsArray}
  googleMapsApiKey="YOUR_API_KEY"
  center={{ lat: 37.7749, lng: -122.4194 }}
  zoom={10}
/>
```

## 🎯 Next Steps

1. Install dependencies: `npm install`
2. Configure environment variables
3. Start development: `npm run dev`
4. Customize theme and colors
5. Add authentication (Firebase Auth, Auth0, etc.)
6. Add real-time updates (WebSocket/Socket.io)
7. Add notification system
8. Implement user roles and permissions

## 💡 Tips

- Use Chrome DevTools for debugging
- Enable React DevTools extension
- Check console for API errors
- Test responsive design in different viewports
- Use Material-UI theme customization for branding

---

**All frontend code is production-ready and fully typed with TypeScript!** 🎉
