#!/usr/bin/env python3
"""
Web Dashboard API for Linux Monitoring Alerts
Provides REST API endpoints and serves the dashboard frontend
"""

import json
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Constants
MAX_STDOUT_CHARS = 2000
MAX_STDERR_CHARS = 1000

# Get project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_DIR = CURRENT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "output"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
MONITOR_SCRIPT = SCRIPTS_DIR / "monitor.sh"

app = FastAPI(
    title="Linux Monitoring Dashboard API",
    description="REST API for Linux system monitoring and alerting",
    version="1.0.0"
)

# Enable CORS for local development
# NOTE: In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_report_files() -> List[Path]:
    """Get all JSON report files sorted by timestamp (newest first)"""
    if not OUTPUT_DIR.exists():
        return []
    
    json_files = list(OUTPUT_DIR.glob("report_*.json"))
    # Sort by filename (which includes timestamp) in descending order
    json_files.sort(reverse=True)
    return json_files


def read_report(filepath: Path) -> Optional[Dict]:
    """Read and parse a JSON report file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading report {filepath}: {e}")
        return None


@app.get("/")
async def root():
    """Serve the main dashboard page"""
    index_file = CURRENT_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Dashboard frontend not found. Please ensure static/index.html exists."}


@app.get("/api/latest")
async def get_latest_report():
    """Get the most recent monitoring report"""
    reports = get_report_files()
    
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")
    
    latest_report = read_report(reports[0])
    
    if latest_report is None:
        raise HTTPException(status_code=500, detail="Failed to read latest report")
    
    # Add filename for reference
    latest_report["filename"] = reports[0].name
    
    return latest_report


@app.get("/api/history")
async def get_history(limit: int = 20):
    """Get historical monitoring reports
    
    Args:
        limit: Maximum number of reports to return (default: 20, max: 100)
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    
    reports = get_report_files()[:limit]
    
    if not reports:
        return {"reports": [], "count": 0}
    
    history = []
    for report_file in reports:
        report = read_report(report_file)
        if report:
            # Add filename
            report["filename"] = report_file.name
            history.append(report)
    
    return {
        "reports": history,
        "count": len(history),
        "total_available": len(get_report_files())
    }


@app.post("/api/run")
async def run_monitor():
    """Trigger the monitoring script and return results
    
    Executes monitor.sh with a timeout and returns the output
    """
    if not MONITOR_SCRIPT.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Monitor script not found at {MONITOR_SCRIPT}"
        )
    
    try:
        # Run the monitor script with a timeout
        process = await asyncio.create_subprocess_exec(
            str(MONITOR_SCRIPT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(SCRIPTS_DIR)
        )
        
        try:
            # Wait for completion with 30 second timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise HTTPException(
                status_code=408,
                detail="Monitor script timed out after 30 seconds"
            )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        # Get the latest report file
        reports = get_report_files()
        latest_filename = reports[0].name if reports else None
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout_text[-MAX_STDOUT_CHARS:] if len(stdout_text) > MAX_STDOUT_CHARS else stdout_text,
            "stderr": stderr_text[-MAX_STDERR_CHARS:] if len(stderr_text) > MAX_STDERR_CHARS else stderr_text,
            "latest_report": latest_filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run monitor script: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics about the monitoring system"""
    reports = get_report_files()
    
    stats = {
        "total_reports": len(reports),
        "oldest_report": reports[-1].name if reports else None,
        "newest_report": reports[0].name if reports else None,
    }
    
    # Get stats from latest report if available
    if reports:
        latest = read_report(reports[0])
        if latest:
            stats["latest_timestamp"] = latest.get("timestamp")
            stats["hostname"] = latest.get("hostname")
            
            # Count alerts by severity
            alerts = latest.get("alerts", [])
            stats["alert_counts"] = {
                "total": len(alerts),
                "critical": sum(1 for a in alerts if a.get("severity") == "critical"),
                "warning": sum(1 for a in alerts if a.get("severity") == "warning"),
            }
    
    return stats


# Mount static files directory
static_dir = CURRENT_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    print("Starting Linux Monitoring Dashboard...")
    print(f"Project directory: {PROJECT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Monitor script: {MONITOR_SCRIPT}")
    print("\nDashboard will be available at: http://localhost:8000")
    print("API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
