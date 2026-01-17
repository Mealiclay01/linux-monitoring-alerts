#!/bin/bash
# Linux Monitoring and Alerting Tool - Main Script
# Collects system metrics, generates reports, and sends alerts

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Use config.yml if it exists, otherwise use config.example.yml
if [[ -f "${PROJECT_DIR}/config/config.yml" ]]; then
    CONFIG_FILE="${PROJECT_DIR}/config/config.yml"
else
    CONFIG_FILE="${PROJECT_DIR}/config/config.example.yml"
fi
OUTPUT_DIR="${PROJECT_DIR}/output"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Timestamp for report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
JSON_REPORT="${OUTPUT_DIR}/report_${TIMESTAMP}.json"

# Function to parse YAML config (simple parser for our use case)
parse_config() {
    local key=$1
    local config_file=$2
    
    if [[ ! -f "$config_file" ]]; then
        echo "Error: Config file not found: $config_file" >&2
        exit 1
    fi
    
    case $key in
        "disk_usage_threshold")
            grep "disk_usage:" "$config_file" | awk '{print $2}'
            ;;
        "ram_usage_threshold")
            grep "ram_usage:" "$config_file" | awk '{print $2}'
            ;;
        "load_average_threshold")
            grep "load_average:" "$config_file" | awk '{print $2}'
            ;;
        "services")
            sed -n '/^services:/,/^[^ ]/p' "$config_file" | grep "^  -" | awk '{print $2}' | tr '\n' ' '
            ;;
    esac
}

# Function to collect disk usage
collect_disk_usage() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "$usage"
}

# Function to collect RAM usage
collect_ram_usage() {
    local total=$(free -m | awk 'NR==2 {print $2}')
    local used=$(free -m | awk 'NR==2 {print $3}')
    local percentage=$(awk "BEGIN {printf \"%.0f\", ($used/$total)*100}")
    echo "$percentage"
}

# Function to collect load average
collect_load_average() {
    local load=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)
    echo "$load"
}

# Function to collect uptime
collect_uptime() {
    local uptime_info=$(uptime -p)
    echo "$uptime_info"
}

# Function to check systemd service status
check_service_status() {
    local service=$1
    local status="unknown"
    local active="unknown"
    
    # Check if service unit file exists
    if systemctl list-unit-files "${service}.service" 2>/dev/null | grep -q "${service}.service"; then
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            active="active"
            status="running"
        else
            active="inactive"
            status="stopped"
        fi
    else
        status="not_installed"
        active="not_installed"
    fi
    
    echo "${status}|${active}"
}

# Function to generate JSON report
generate_json_report() {
    local disk_usage=$1
    local ram_usage=$2
    local load_avg=$3
    local uptime_info=$4
    local services_status=$5
    local alerts=$6
    
    cat > "$JSON_REPORT" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "metrics": {
    "disk_usage": {
      "value": $disk_usage,
      "unit": "percent",
      "filesystem": "/"
    },
    "ram_usage": {
      "value": $ram_usage,
      "unit": "percent"
    },
    "load_average": {
      "1min": $load_avg
    },
    "uptime": {
      "value": "$uptime_info"
    }
  },
  "services": [
$services_status
  ],
  "alerts": [
$alerts
  ]
}
EOF
}

# Function to send Telegram alert
send_telegram_alert() {
    local message=$1
    local bot_token="${TELEGRAM_BOT_TOKEN:-}"
    local chat_id="${TELEGRAM_CHAT_ID:-}"
    
    if [[ -z "$bot_token" ]] || [[ -z "$chat_id" ]]; then
        echo "Warning: Telegram credentials not set. Skipping alert." >&2
        return 0
    fi
    
    local url="https://api.telegram.org/bot${bot_token}/sendMessage"
    
    curl -s -X POST "$url" \
        -d "chat_id=${chat_id}" \
        -d "text=${message}" \
        -d "parse_mode=HTML" > /dev/null || {
        echo "Warning: Failed to send Telegram alert" >&2
        return 1
    }
}

# Main execution
main() {
    echo "=== Linux Monitoring and Alerting Tool ==="
    echo "Collecting system metrics..."
    
    # Read thresholds from config
    DISK_THRESHOLD=$(parse_config "disk_usage_threshold" "$CONFIG_FILE")
    RAM_THRESHOLD=$(parse_config "ram_usage_threshold" "$CONFIG_FILE")
    LOAD_THRESHOLD=$(parse_config "load_average_threshold" "$CONFIG_FILE")
    SERVICES_LIST=$(parse_config "services" "$CONFIG_FILE")
    
    # Collect metrics
    DISK_USAGE=$(collect_disk_usage)
    RAM_USAGE=$(collect_ram_usage)
    LOAD_AVG=$(collect_load_average)
    UPTIME_INFO=$(collect_uptime)
    
    echo "Disk Usage: ${DISK_USAGE}%"
    echo "RAM Usage: ${RAM_USAGE}%"
    echo "Load Average: ${LOAD_AVG}"
    echo "Uptime: ${UPTIME_INFO}"
    
    # Check services
    echo "Checking services..."
    services_json=""
    first_service=true
    for service in $SERVICES_LIST; do
        service_info=$(check_service_status "$service")
        status=$(echo "$service_info" | cut -d'|' -f1)
        active=$(echo "$service_info" | cut -d'|' -f2)
        
        if [ "$first_service" = true ]; then
            first_service=false
        else
            services_json="${services_json},"
        fi
        
        services_json="${services_json}
    {
      \"name\": \"$service\",
      \"status\": \"$status\",
      \"active\": \"$active\"
    }"
        
        echo "  - $service: $status ($active)"
    done
    
    # Check thresholds and generate alerts
    echo "Checking thresholds..."
    alerts=""
    alert_messages=()
    first_alert=true
    
    if (( DISK_USAGE > DISK_THRESHOLD )); then
        alert_msg="⚠️ ALERT: Disk usage at ${DISK_USAGE}% (threshold: ${DISK_THRESHOLD}%)"
        echo "$alert_msg"
        alert_messages+=("$alert_msg")
        
        if [ "$first_alert" = true ]; then
            first_alert=false
        else
            alerts="${alerts},"
        fi
        alerts="${alerts}
    {
      \"type\": \"disk_usage\",
      \"severity\": \"warning\",
      \"message\": \"Disk usage at ${DISK_USAGE}% exceeds threshold of ${DISK_THRESHOLD}%\"
    }"
    fi
    
    if (( RAM_USAGE > RAM_THRESHOLD )); then
        alert_msg="⚠️ ALERT: RAM usage at ${RAM_USAGE}% (threshold: ${RAM_THRESHOLD}%)"
        echo "$alert_msg"
        alert_messages+=("$alert_msg")
        
        if [ "$first_alert" = true ]; then
            first_alert=false
        else
            alerts="${alerts},"
        fi
        alerts="${alerts}
    {
      \"type\": \"ram_usage\",
      \"severity\": \"warning\",
      \"message\": \"RAM usage at ${RAM_USAGE}% exceeds threshold of ${RAM_THRESHOLD}%\"
    }"
    fi
    
    # Load average comparison (handle floating point using awk)
    load_exceeds=$(awk -v loadval="$LOAD_AVG" -v threshold="$LOAD_THRESHOLD" 'BEGIN {print (loadval > threshold)}')
    if [[ "$load_exceeds" == "1" ]]; then
        alert_msg="⚠️ ALERT: Load average at ${LOAD_AVG} (threshold: ${LOAD_THRESHOLD})"
        echo "$alert_msg"
        alert_messages+=("$alert_msg")
        
        if [ "$first_alert" = true ]; then
            first_alert=false
        else
            alerts="${alerts},"
        fi
        alerts="${alerts}
    {
      \"type\": \"load_average\",
      \"severity\": \"warning\",
      \"message\": \"Load average at ${LOAD_AVG} exceeds threshold of ${LOAD_THRESHOLD}\"
    }"
    fi
    
    # Check for stopped services
    for service in $SERVICES_LIST; do
        service_info=$(check_service_status "$service")
        status=$(echo "$service_info" | cut -d'|' -f1)
        
        if [[ "$status" != "running" ]] && [[ "$status" != "not_installed" ]]; then
            alert_msg="⚠️ ALERT: Service $service is $status"
            echo "$alert_msg"
            alert_messages+=("$alert_msg")
            
            if [ "$first_alert" = true ]; then
                first_alert=false
            else
                alerts="${alerts},"
            fi
            alerts="${alerts}
    {
      \"type\": \"service_down\",
      \"severity\": \"critical\",
      \"message\": \"Service $service is $status\",
      \"service\": \"$service\"
    }"
        fi
    done
    
    # Generate JSON report
    echo "Generating JSON report..."
    generate_json_report "$DISK_USAGE" "$RAM_USAGE" "$LOAD_AVG" "$UPTIME_INFO" "$services_json" "$alerts"
    echo "JSON report saved to: $JSON_REPORT"
    
    # Generate HTML report
    if command -v python3 &> /dev/null; then
        echo "Generating HTML report..."
        HTML_REPORT="${OUTPUT_DIR}/report_${TIMESTAMP}.html"
        python3 "${SCRIPT_DIR}/generate_html_report.py" "$JSON_REPORT" "$HTML_REPORT"
        echo "HTML report saved to: $HTML_REPORT"
    else
        echo "Python3 not found. Skipping HTML report generation."
    fi
    
    # Send Telegram alerts
    if [ ${#alert_messages[@]} -gt 0 ]; then
        echo "Sending Telegram alerts..."
        combined_message="<b>🚨 Linux Monitoring Alert - $(hostname)</b>%0A%0A"
        for msg in "${alert_messages[@]}"; do
            combined_message="${combined_message}${msg}%0A"
        done
        combined_message="${combined_message}%0ATimestamp: $(date)"
        
        send_telegram_alert "$combined_message"
    else
        echo "No alerts triggered."
    fi
    
    echo "Monitoring complete!"
}

# Run main function
main "$@"
