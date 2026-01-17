#!/usr/bin/env python3
"""
HTML Report Generator for Linux Monitoring Tool
Converts JSON report to a simple HTML format
"""

import json
import sys
import html

def generate_html_report(json_file, html_file):
    """Generate an HTML report from JSON data"""
    
    # Read JSON report
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Extract data
    timestamp = data.get('timestamp', '')
    hostname = data.get('hostname', 'Unknown')
    metrics = data.get('metrics', {})
    services = data.get('services', [])
    alerts = data.get('alerts', [])
    
    # Escape values for safe HTML insertion
    hostname_escaped = html.escape(hostname)
    timestamp_escaped = html.escape(timestamp)
    
    # Determine overall status
    overall_status = "OK" if len(alerts) == 0 else "WARNING"
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linux Monitoring Report - {hostname_escaped}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 3px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status.ok {{
            background-color: #4CAF50;
            color: white;
        }}
        .status.warning {{
            background-color: #f44336;
            color: white;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-name {{
            font-weight: bold;
            color: #555;
        }}
        .metric-value {{
            color: #333;
        }}
        .service {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
            border-radius: 3px;
        }}
        .service-name {{
            font-weight: bold;
        }}
        .service-status {{
            padding: 2px 10px;
            border-radius: 3px;
            font-size: 12px;
        }}
        .service-status.running {{
            background-color: #4CAF50;
            color: white;
        }}
        .service-status.stopped {{
            background-color: #f44336;
            color: white;
        }}
        .service-status.not_installed {{
            background-color: #999;
            color: white;
        }}
        .alert {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 3px;
            border-left: 4px solid;
        }}
        .alert.warning {{
            background-color: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }}
        .alert.critical {{
            background-color: #f8d7da;
            border-color: #f44336;
            color: #721c24;
        }}
        .alert-type {{
            font-weight: bold;
            text-transform: uppercase;
            font-size: 12px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Linux Monitoring Report</h1>
        <p>Hostname: <strong>{hostname_escaped}</strong> 
           <span class="status {overall_status.lower()}">{overall_status}</span>
        </p>
        <p style="font-size: 14px; margin: 5px 0 0 0;">Generated: {timestamp_escaped}</p>
    </div>

    <div class="section">
        <h2>System Metrics</h2>
"""
    
    # Add disk usage
    disk_usage = metrics.get('disk_usage', {})
    html_content += f"""
        <div class="metric">
            <span class="metric-name">Disk Usage ({disk_usage.get('filesystem', '/')})</span>
            <span class="metric-value">{disk_usage.get('value', 'N/A')}%</span>
        </div>
"""
    
    # Add RAM usage
    ram_usage = metrics.get('ram_usage', {})
    html_content += f"""
        <div class="metric">
            <span class="metric-name">RAM Usage</span>
            <span class="metric-value">{ram_usage.get('value', 'N/A')}%</span>
        </div>
"""
    
    # Add load average
    load_avg = metrics.get('load_average', {})
    html_content += f"""
        <div class="metric">
            <span class="metric-name">Load Average (1 min)</span>
            <span class="metric-value">{load_avg.get('1min', 'N/A')}</span>
        </div>
"""
    
    # Add uptime
    uptime = metrics.get('uptime', {})
    html_content += f"""
        <div class="metric">
            <span class="metric-name">Uptime</span>
            <span class="metric-value">{uptime.get('value', 'N/A')}</span>
        </div>
    </div>
"""
    
    # Add services section
    html_content += """
    <div class="section">
        <h2>Service Status</h2>
"""
    
    if services:
        for service in services:
            name = service.get('name', 'Unknown')
            status = service.get('status', 'unknown')
            name_escaped = html.escape(name)
            status_escaped = html.escape(status)
            html_content += f"""
        <div class="service">
            <span class="service-name">{name_escaped}</span>
            <span class="service-status {status}">{status_escaped.upper()}</span>
        </div>
"""
    else:
        html_content += "<p>No services configured for monitoring.</p>"
    
    html_content += """
    </div>
"""
    
    # Add alerts section
    html_content += """
    <div class="section">
        <h2>Alerts</h2>
"""
    
    if alerts:
        for alert in alerts:
            severity = alert.get('severity', 'warning')
            alert_type = alert.get('type', 'unknown')
            message = alert.get('message', '')
            severity_escaped = html.escape(severity)
            alert_type_escaped = html.escape(alert_type)
            message_escaped = html.escape(message)
            html_content += f"""
        <div class="alert {severity}">
            <div class="alert-type">{severity_escaped}: {alert_type_escaped}</div>
            <div>{message_escaped}</div>
        </div>
"""
    else:
        html_content += '<p style="color: green; font-weight: bold;">✓ No alerts - All systems operating normally</p>'
    
    html_content += """
    </div>

    <div class="footer">
        <p>Linux Monitoring and Alerting Tool | Generated automatically</p>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report generated successfully: {html_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_html_report.py <json_file> <html_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    html_file = sys.argv[2]
    
    try:
        generate_html_report(json_file, html_file)
    except Exception as e:
        print(f"Error generating HTML report: {e}", file=sys.stderr)
        sys.exit(1)
