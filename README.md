# Linux Monitoring and Alerting Tool

A comprehensive Linux server monitoring and alerting tool built with Bash scripts. Monitors system metrics, checks service status, generates reports, and sends alerts via Telegram. **Now with a modern web dashboard!**

## Features

- **System Metrics Monitoring**
  - Disk usage (percentage)
  - RAM usage (percentage)
  - Load average (1-minute)
  - System uptime
  
- **Service Monitoring**
  - Monitor systemd services (SSH, Nginx, MySQL, etc.)
  - Configurable service list
  - Robust detection when systemd is unavailable (containers/Codespaces)
  - Falls back to SysV `service`/`/etc/init.d` checks or `pgrep` heuristics
  
- **Web Dashboard** 🎨 **NEW!**
  - Modern, responsive UI with dark mode toggle
  - Real-time metrics display
  - Service status with color-coded badges
  - Alert monitoring with severity levels
  - Historical trend charts (disk, RAM, load average)
  - Auto-refresh every 5 seconds
  - Manual refresh and "Run Now" buttons
  - REST API for programmatic access
  
- **Reporting**
  - JSON reports saved to `output/` directory
  - HTML reports (optional, requires Python 3)
  
- **Alerting**
  - Telegram notifications for threshold violations
  - Service down alerts
  - Configurable thresholds

- **Automation**
  - Systemd timer for periodic execution
  - Runs every 5 minutes by default

## Requirements

- Linux system (systemd optional - works in containers)
- Bash 4.0+
- Basic utilities: `df`, `free`, `uptime`, `awk`
- `curl` (for Telegram alerts)
- Python 3.8+ (for HTML reports and web dashboard)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mealiclay01/linux-monitoring-alerts.git
cd linux-monitoring-alerts
```

### 2. Configure Thresholds and Services

Edit the configuration file to set your monitoring thresholds and services:

```bash
cp config/config.example.yml config/config.yml
nano config/config.yml
```

Example configuration:

```yaml
# Threshold configurations
thresholds:
  disk_usage: 80       # Alert when disk usage exceeds 80%
  ram_usage: 85        # Alert when RAM usage exceeds 85%
  load_average: 4.0    # Alert when 1-min load average exceeds 4.0

# Services to monitor
services:
  - ssh
  - nginx
  - mysql
```

### 3. Set Up Telegram Bot (Optional)

To receive alerts via Telegram, follow the detailed guide in [docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md).

Quick summary:

1. Create a Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID (use [@userinfobot](https://t.me/userinfobot))
4. Set environment variables or a systemd `EnvironmentFile`:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

For persistent configuration, add these to `/etc/environment` or create a systemd environment file. The script will warn and continue if credentials are missing.

### 4. Install Systemd Service (Optional)

For automatic monitoring with systemd timer:

```bash
# Copy files to /opt (or your preferred location)
sudo mkdir -p /opt/linux-monitoring-alerts
sudo cp -r . /opt/linux-monitoring-alerts/

# Make scripts executable
sudo chmod +x /opt/linux-monitoring-alerts/scripts/monitor.sh
sudo chmod +x /opt/linux-monitoring-alerts/scripts/generate_html_report.py

# Copy systemd files
sudo cp systemd/linux-monitoring.service /etc/systemd/system/
sudo cp systemd/linux-monitoring.timer /etc/systemd/system/

# Edit service file to add Telegram credentials (optional)
sudo nano /etc/systemd/system/linux-monitoring.service
# Uncomment and set the Environment lines with your Telegram credentials

# Reload systemd and enable the timer
sudo systemctl daemon-reload
sudo systemctl enable linux-monitoring.timer
sudo systemctl start linux-monitoring.timer
```

## Usage

### Web Dashboard (Recommended) 🎨

The easiest way to monitor your system is through the web dashboard:

1. **Install Python dependencies:**
   ```bash
   cd dashboard
   pip3 install -r requirements.txt
   ```

2. **Start the dashboard server:**
   ```bash
   python3 app.py
   ```
   
   Or run from project root:
   ```bash
   cd /path/to/linux-monitoring-alerts
   python3 dashboard/app.py
   ```

3. **Access the dashboard:**
   Open your browser and navigate to `http://localhost:8000`

4. **Dashboard features:**
   - View real-time system metrics (disk, RAM, load, uptime)
   - Monitor service status with color-coded badges
   - See active alerts with severity levels
   - View historical trends with interactive charts
   - Auto-refresh every 5 seconds (configurable)
   - Click "Run Now" to trigger monitoring on-demand
   - Click "Refresh" to manually update the display

5. **API Endpoints:**
   - `GET /api/latest` - Get the most recent report
   - `GET /api/history?limit=20` - Get historical reports
   - `POST /api/run` - Trigger monitor script and get results
   - `GET /api/stats` - Get system statistics
   - Full API documentation at `http://localhost:8000/docs`

> **Tip:** If no reports exist yet, the dashboard will show a helpful message. Run `./scripts/monitor.sh` once (or use **Run Now**) to generate data.

### Containers/Codespaces Behavior

When systemd is not PID 1 (common in containers/Codespaces), the script:

- Detects that systemd is unavailable using PID 1 and `systemctl` health checks.
- Falls back to `/etc/init.d/<service>` or `service <service> status` when available.
- Uses `pgrep` as a heuristic if no init system is present.
- Reports status as `unknown` if it cannot confidently determine service state.
- Avoids emitting service-down alerts unless the service is confidently stopped.

### Manual Execution

Run the monitoring script manually:

```bash
cd scripts
chmod +x monitor.sh
./monitor.sh
```

### Check Timer Status

If using systemd timer:

```bash
# Check timer status
sudo systemctl status linux-monitoring.timer

# View logs
sudo journalctl -u linux-monitoring.service -f

# Check next run time
systemctl list-timers linux-monitoring.timer
```

### View Reports

Reports are saved in the `output/` directory:

- JSON reports: `output/report_YYYYMMDD_HHMMSS.json`
- HTML reports: `output/report_YYYYMMDD_HHMMSS.html`

Example JSON report:

```json
{
  "timestamp": "2024-01-01T00:00:00+00:00",
  "hostname": "server01",
  "metrics": {
    "disk_usage": {
      "value": 45,
      "unit": "percent",
      "filesystem": "/"
    },
    "ram_usage": {
      "value": 62,
      "unit": "percent"
    },
    "load_average": {
      "1min": 1.25
    },
    "uptime": {
      "value": "up 3 days, 5 hours, 23 minutes"
    }
  },
  "services": [
    {
      "name": "ssh",
      "status": "running",
      "active": "active"
    }
  ],
  "alerts": []
}
```

## Configuration Reference

### config/config.example.yml

```yaml
thresholds:
  disk_usage: 80          # Percentage (0-100)
  ram_usage: 85           # Percentage (0-100)
  load_average: 4.0       # Number (typical: 1-core = 1.0)

services:
  - ssh                   # Systemd service names
  - nginx
  - mysql
```

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (from @BotFather)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (from @userinfobot)

## Customization

### Adjust Timer Interval

Edit `/etc/systemd/system/linux-monitoring.timer`:

```ini
[Timer]
# Run every 10 minutes instead of 5
OnUnitActiveSec=10min
```

Then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart linux-monitoring.timer
```

### Monitor Additional Services

Add more services to `config/config.yml`:

```yaml
services:
  - ssh
  - nginx
  - mysql
  - postgresql
  - docker
  - apache2
```

### Adjust Thresholds

Modify thresholds in `config/config.yml` based on your server capacity:

```yaml
thresholds:
  disk_usage: 90      # More lenient
  ram_usage: 95       # More lenient
  load_average: 8.0   # For 8-core server
```

## Troubleshooting

### Script Fails to Execute

Ensure scripts are executable:

```bash
chmod +x scripts/monitor.sh
chmod +x scripts/generate_html_report.py
```

### Telegram Alerts Not Sending

1. Check if environment variables are set:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

2. Test Telegram API manually:
   ```bash
   curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=Test message"
   ```

3. Check service logs:
   ```bash
   sudo journalctl -u linux-monitoring.service -n 50
   ```

### Service Status Shows "not_installed"

The service is not installed on your system. Either:
- Install the service: `sudo apt install nginx` (for Debian/Ubuntu)
- Remove it from the configuration if not needed

### Service Status Shows "unknown"

This is normal in environments without systemd (containers, Codespaces). The monitoring system handles this gracefully and won't trigger false alerts.

### HTML Report Not Generated

Ensure Python 3 is installed:

```bash
python3 --version
```

If not installed:
```bash
sudo apt install python3  # Debian/Ubuntu
sudo yum install python3  # CentOS/RHEL
```

### Dashboard Not Loading

1. **Check Python dependencies:**
   ```bash
   cd dashboard
   pip3 install -r requirements.txt
   ```

2. **Verify the server is running:**
   ```bash
   python3 dashboard/app.py
   ```
   Should show: `Uvicorn running on http://0.0.0.0:8000`

3. **Check if port 8000 is in use:**
   ```bash
   lsof -i :8000
   # Or try a different port
   uvicorn dashboard.app:app --host 0.0.0.0 --port 8080
   ```

4. **Verify reports exist:**
   ```bash
   ls -lh output/
   # Should show report_*.json files
   # If empty, run: ./scripts/monitor.sh
   ```

## File Structure

```
linux-monitoring-alerts/
├── config/
│   └── config.example.yml      # Configuration template
├── dashboard/                   # Web dashboard (NEW!)
│   ├── app.py                  # FastAPI backend server
│   ├── requirements.txt        # Python dependencies
│   └── static/
│       └── index.html          # Dashboard frontend
├── output/                      # Generated reports (created automatically)
│   ├── report_*.json
│   └── report_*.html
├── scripts/
│   ├── monitor.sh              # Main monitoring script
│   ├── generate_html_report.py # HTML report generator
│   └── test_demo.sh            # Test/demo script
├── systemd/
│   ├── linux-monitoring.service # Systemd service unit
│   └── linux-monitoring.timer   # Systemd timer unit
├── .gitignore
├── LICENSE
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the terms of the LICENSE file included in this repository.

## Security Notes

- Store Telegram credentials securely (use environment variables or systemd environment files)
- Never commit sensitive credentials to version control
- The monitoring script runs with limited privileges when using systemd security settings
- Review and adjust systemd security settings based on your requirements

## Author

Mealiclay01

## Acknowledgments

Built with standard Linux utilities and Bash scripting for maximum compatibility and minimal dependencies.
