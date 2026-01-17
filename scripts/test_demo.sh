#!/bin/bash
# Test script to demonstrate the Linux Monitoring and Alerting Tool
# This script will run the monitor with example configuration

set -euo pipefail

echo "===== Linux Monitoring and Alerting Tool - Test Demo ====="
echo ""
echo "This test will:"
echo "1. Run the monitoring script"
echo "2. Generate JSON and HTML reports"
echo "3. Display the results"
echo ""
echo "Press Enter to continue..."
read

cd "$(dirname "$0")/.."

echo "Running monitoring script..."
echo "=============================================="
./scripts/monitor.sh

echo ""
echo "=============================================="
echo "Reports generated in output/ directory:"
echo ""
ls -lh output/*.{json,html} 2>/dev/null || echo "No reports found"

echo ""
echo "Latest JSON report contents:"
echo "=============================================="
latest_json=$(ls -t output/*.json 2>/dev/null | head -1)
if [ -n "$latest_json" ]; then
    cat "$latest_json"
else
    echo "No JSON report found"
fi

echo ""
echo "=============================================="
echo "Test completed!"
echo ""
echo "To view the HTML report, open:"
latest_html=$(ls -t output/*.html 2>/dev/null | head -1)
if [ -n "$latest_html" ]; then
    echo "  $latest_html"
    echo ""
    echo "in your web browser."
else
    echo "  No HTML report found"
fi
