# Linux Monitoring and Alerting Tool

A comprehensive Linux server monitoring and alerting tool built with Bash scripts. Monitors system metrics, checks service status, generates reports, and sends alerts via Telegram.

## Features

- **System Metrics Monitoring**
  - Disk usage (percentage)
  - RAM usage (percentage)
  - Load average (1-minute)
  - System uptime
  
- **Service Monitoring**
  - Monitor systemd services (SSH, Nginx, MySQL, etc.)
  - Configurable service list
  
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

- Linux system with systemd
- Bash 4.0+
- Basic utilities: `df`, `free`, `uptime`, `awk`
- `curl` (for Telegram alerts)
- Python 3 (optional, for HTML report generation)

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

To receive alerts via Telegram:

1. Create a Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID (use [@userinfobot](https://t.me/userinfobot))
4. Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

For persistent configuration, add these to `/etc/environment` or create a systemd environment file.

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
  "timestamp": "2026-01-17T05:30:00+00:00",
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

## File Structure

```
linux-monitoring-alerts/
├── config/
│   └── config.example.yml      # Configuration template
├── output/                      # Generated reports (created automatically)
│   ├── report_*.json
│   └── report_*.html
├── scripts/
│   ├── monitor.sh              # Main monitoring script
│   └── generate_html_report.py # HTML report generator
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
