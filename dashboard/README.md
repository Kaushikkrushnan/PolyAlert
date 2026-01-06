# PolyAlert Dashboard - Frontend

React-based admin dashboard for the PolyAlert disaster alert system.

## Features

- **Dashboard Overview**: Real-time statistics and system status
- **Alert Management**: View, create, and manage alerts
- **Interactive Map**: Visualize alerts on Google Maps with affected radius
- **Multi-language Support**: Create alerts in multiple languages
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- PolyAlert backend API running (default: http://localhost:8080)
- Google Maps API key (for map features)

### Installation

```bash
cd dashboard
npm install
```

### Configuration

Create a `.env` file in the dashboard directory:

```env
REACT_APP_API_URL=http://localhost:8080
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Development

```bash
npm run dev
```

The dashboard will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

The build artifacts will be in the `build/` directory.

## Components

### Dashboard
Main overview page with statistics:
- Total alerts count
- Active alerts
- Critical alerts requiring attention
- Resolved alerts
- Alerts by type and severity charts
- System status indicators

### Alert List
View and manage all alerts:
- Real-time auto-refresh (every 30 seconds)
- Filter by severity and type
- View detailed alert information
- Delete alerts

### Alert Form
Create new disaster alerts:
- 10 alert types (earthquake, flood, fire, etc.)
- 5 severity levels
- Location data (coordinates, city, region, country)
- Multi-language targeting
- Custom metadata support

### Alert Map
Interactive Google Maps visualization:
- Pin markers for each alert
- Color-coded by severity
- Click markers for details
- Visual affected radius
- Auto-fit bounds to show all alerts

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI (MUI)** - Component library
- **React Router** - Navigation
- **Google Maps React** - Map integration
- **Vite** - Build tool
- **Axios** - HTTP client

## API Integration

The dashboard connects to the PolyAlert backend API:

```typescript
// Example: Fetch alerts
const response = await fetch(`${API_URL}/api/v1/alerts`);
const alerts = await response.json();

// Example: Create alert
await fetch(`${API_URL}/api/v1/alerts`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(alertData),
});
```

## Deployment

### Firebase Hosting

```bash
npm run build
firebase deploy --only hosting
```

### Docker

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Customization

### Theme
Modify `src/App.tsx` to customize colors:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
  },
});
```

### Alert Types
Add new alert types in `src/components/AlertForm.tsx`:

```typescript
const ALERT_TYPES = [
  { value: 'custom_type', label: '🔔 Custom Alert', emoji: '🔔' },
  // ... more types
];
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run `npm run lint` and `npm run format`
5. Submit a pull request

## License

MIT License - See LICENSE file for details
