# Linux Monitoring and Alerting Tool - Implementation Summary

## Overview
A comprehensive Linux server monitoring and alerting tool built with Bash scripts, Python for HTML report generation, and systemd for automation. Sends alerts via Telegram when thresholds are exceeded or services are down.

## Files Created

### Configuration
- `config/config.example.yml` - Example configuration with thresholds and services to monitor

### Scripts
- `scripts/monitor.sh` - Main monitoring script (Bash)
  - Collects disk usage, RAM usage, load average, uptime
  - Checks systemd service status
  - Generates JSON reports
  - Triggers HTML report generation
  - Sends Telegram alerts when thresholds are exceeded
  
- `scripts/generate_html_report.py` - HTML report generator (Python 3)
  - Converts JSON reports to styled HTML
  - Displays metrics, services, and alerts
  
- `scripts/test_demo.sh` - Interactive test/demo script

### Systemd Integration
- `systemd/linux-monitoring.service` - Systemd service unit
- `systemd/linux-monitoring.timer` - Systemd timer (runs every 5 minutes)

### Documentation
- `README.md` - Comprehensive setup and usage guide
- `docs/TELEGRAM_SETUP.md` - Telegram bot configuration guide

### Output
- `output/.gitkeep` - Keeps the output directory in git
- Generated reports saved here (excluded from git)

## Features Implemented

### ✅ System Metrics Collection
- Disk usage (percentage for root filesystem)
- RAM usage (percentage)
- Load average (1-minute)
- System uptime

### ✅ Service Monitoring
- Configurable systemd service monitoring
- Detects running, stopped, and not installed services
- Default services: ssh, nginx, mysql (fully configurable)

### ✅ Configuration Management
- YAML-based configuration
- Configurable thresholds for all metrics
- Configurable service list
- Falls back to config.example.yml if config.yml doesn't exist

### ✅ Reporting
- JSON reports with structured data
- HTML reports with styled interface
- Timestamped reports for historical tracking
- Reports include all metrics, service status, and alerts

### ✅ Alerting
- Telegram bot integration
- Environment variable configuration (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
- Alerts for:
  - Disk usage exceeding threshold
  - RAM usage exceeding threshold
  - Load average exceeding threshold
  - Services that are down
- Proper URL encoding for message safety

### ✅ Automation
- Systemd service and timer
- Runs every 5 minutes by default
- Persistent across reboots
- Logging to systemd journal

### ✅ Security
- No hardcoded credentials
- Environment variable based configuration
- Systemd security settings (NoNewPrivileges, PrivateTmp)
- Proper URL encoding to prevent injection
- No security vulnerabilities found by CodeQL

## Testing

All features have been tested:
- ✅ Metrics collection works correctly
- ✅ Service detection works for running, stopped, and not installed services
- ✅ JSON reports are valid and well-formed
- ✅ HTML reports render correctly
- ✅ Alert thresholds trigger correctly
- ✅ Telegram integration ready (requires credentials to fully test)
- ✅ Configuration parsing works
- ✅ Error handling in place
- ✅ URL encoding works correctly

## Usage

### Quick Start
```bash
# Copy and customize config
cp config/config.example.yml config/config.yml
nano config/config.yml

# Run manually
./scripts/monitor.sh

# View reports
ls -lh output/
```

### With Telegram Alerts
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
./scripts/monitor.sh
```

### Install as Systemd Service
```bash
sudo cp -r . /opt/linux-monitoring-alerts
sudo cp systemd/*.service systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now linux-monitoring.timer
```

## Dependencies
- Bash 4.0+
- Standard Linux utilities: df, free, uptime, awk
- curl (for Telegram alerts)
- Python 3 (optional, for HTML reports)
- systemd (for automation)

## Code Quality
- ✅ Error handling with set -euo pipefail
- ✅ Proper URL encoding for security
- ✅ No unused variables
- ✅ Clean, readable code
- ✅ Comprehensive documentation
- ✅ No security vulnerabilities (CodeQL verified)

## Future Enhancements (Not in Scope)
- Email alerts
- Multiple alert channels
- Historical data storage
- Graphical dashboards
- Custom check scripts
- Multi-server monitoring
- Alert acknowledgment system
