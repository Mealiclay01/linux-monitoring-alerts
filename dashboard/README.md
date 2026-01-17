# Web Dashboard Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   cd dashboard
   pip3 install -r requirements.txt
   ```

2. **Generate some monitoring data:**
   ```bash
   cd ..
   ./scripts/monitor.sh
   ```

## Running the Dashboard

**From the project root:**
```bash
python3 dashboard/app.py
```

**From the dashboard directory:**
```bash
cd dashboard
python3 app.py
```

## Accessing the Dashboard

Open your browser and navigate to:
- **Dashboard:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Features

### Metrics Display
- **Disk Usage:** Real-time percentage of disk space used
- **RAM Usage:** Real-time memory utilization
- **Load Average:** 1-minute load average
- **System Uptime:** How long the system has been running

### Services Monitoring
- Color-coded status badges:
  - 🟢 **Green (Running):** Service is active
  - 🔴 **Red (Stopped):** Service is inactive
  - 🟡 **Yellow (Not Installed):** Service not found
  - ⚪ **Gray (Unknown):** Systemd not available

### Alerts
- **Critical:** Service down alerts (red badge)
- **Warning:** Threshold violation alerts (yellow badge)

### Historical Charts
- **Disk Usage Over Time:** Track disk space trends
- **RAM Usage Over Time:** Monitor memory consumption
- **Load Average Over Time:** View system load patterns

### Controls
- **🔄 Refresh:** Manually update all data
- **▶ Run Now:** Execute monitoring script immediately
- **Auto-refresh:** Updates every 5 seconds automatically

## API Endpoints

### GET /api/latest
Returns the most recent monitoring report.

**Example:**
```bash
curl http://localhost:8000/api/latest
```

### GET /api/history?limit=N
Returns the last N monitoring reports (max 100).

**Example:**
```bash
curl http://localhost:8000/api/history?limit=10
```

### POST /api/run
Triggers the monitoring script and returns execution results.

**Example:**
```bash
curl -X POST http://localhost:8000/api/run
```

### GET /api/stats
Returns overall statistics about the monitoring system.

**Example:**
```bash
curl http://localhost:8000/api/stats
```

## Troubleshooting

### Dashboard shows "Failed to load monitoring data"
- Ensure the monitor script has run at least once: `./scripts/monitor.sh`
- Check that JSON files exist in `output/` directory
- Verify the API is running on port 8000

### Charts not displaying
- Wait for at least 2 data points (run monitor script twice)
- Check browser console for errors
- Ensure report files are valid JSON

### Port 8000 already in use
Run on a different port:
```bash
uvicorn dashboard.app:app --host 0.0.0.0 --port 8080
```

## Production Deployment

For production use:

1. **Update CORS settings** in `dashboard/app.py` to restrict origins
2. **Use a reverse proxy** (nginx, Apache) for HTTPS
3. **Set up systemd service** for auto-start
4. **Configure firewall** to allow access to the dashboard port
5. **Use environment variables** for configuration

Example systemd service:
```ini
[Unit]
Description=Linux Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=monitoring
WorkingDirectory=/opt/linux-monitoring-alerts
ExecStart=/usr/bin/python3 dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Notes

- The dashboard is designed for **local/internal use**
- CORS is currently set to allow all origins (development only)
- No authentication is implemented by default
- For external access, add authentication and use HTTPS
- Keep Python dependencies up to date

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review the [Troubleshooting](#troubleshooting) section
- Open an issue on GitHub
