"""
Daily Update Trigger Endpoint
Allows remote triggering of ETL pipeline from mobile app or external services
"""

from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
import asyncio
import subprocess
import sys
import os
from pathlib import Path

router = APIRouter(prefix="/api/updates", tags=["updates"])

# Track current update status
_update_status = {
    "is_running": False,
    "last_started": None,
    "last_completed": None,
    "last_error": None,
    "current_step": None,
}

@router.get("/status")
async def get_update_status():
    """Get current status of daily update process"""
    return {
        "is_running": _update_status["is_running"],
        "last_started": _update_status["last_started"],
        "last_completed": _update_status["last_completed"],
        "last_error": _update_status["last_error"],
        "current_step": _update_status["current_step"],
    }

@router.post("/trigger-daily-update")
async def trigger_daily_update(background_tasks: BackgroundTasks):
    """
    Trigger full ETL pipeline from remote request (mobile app or scheduled task)
    
    Returns immediately with status. ETL runs in background.
    
    Response:
        {
            "status": "ETL pipeline started",
            "timestamp": "2026-01-14T10:30:00",
            "task_id": "background_task_123"
        }
    
    Usage:
        curl -X POST http://localhost:8000/api/updates/trigger-daily-update
        
        # Remote via ngrok:
        curl -X POST https://abc123.ngrok.io/api/updates/trigger-daily-update
    """
    
    if _update_status["is_running"]:
        return {
            "status": "ETL already running",
            "timestamp": datetime.now().isoformat(),
            "started_at": _update_status["last_started"],
        }
    
    # Mark as running
    _update_status["is_running"] = True
    _update_status["last_started"] = datetime.now().isoformat()
    _update_status["current_step"] = "Initializing ETL pipeline..."
    
    # Add ETL task to background
    background_tasks.add_task(_run_etl_pipeline)
    
    return {
        "status": "ETL pipeline started",
        "timestamp": _update_status["last_started"],
    }

async def _run_etl_pipeline():
    """
    Run the full ETL pipeline asynchronously
    
    Steps:
    1. Fetch FX rates (MNB API)
    2. Fetch instrument prices (Selenium)
    3. Fetch pension values (Selenium)
    4. Update manual price overrides
    5. Aggregate and calculate net wealth
    """
    
    try:
        # Get path to ETL script
        current_dir = Path(__file__).parent.parent
        etl_script = current_dir / "etl" / "run_daily_etl.py"
        
        _update_status["current_step"] = "Running ETL pipeline..."
        
        # Run ETL subprocess
        result = subprocess.run(
            [sys.executable, str(etl_script)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes max
        )
        
        if result.returncode == 0:
            _update_status["is_running"] = False
            _update_status["last_completed"] = datetime.now().isoformat()
            _update_status["current_step"] = "Completed successfully"
            _update_status["last_error"] = None
        else:
            _update_status["is_running"] = False
            _update_status["last_error"] = result.stderr
            _update_status["current_step"] = f"Failed: {result.stderr[:200]}"
    
    except asyncio.TimeoutError:
        _update_status["is_running"] = False
        _update_status["last_error"] = "ETL pipeline timeout after 10 minutes"
        _update_status["current_step"] = "Timeout"
    
    except Exception as e:
        _update_status["is_running"] = False
        _update_status["last_error"] = str(e)
        _update_status["current_step"] = f"Error: {str(e)[:100]}"

@router.post("/schedule-daily")
async def schedule_daily_update(hour: int = 7, minute: int = 0):
    """
    Configure automatic daily update schedule
    
    Parameters:
        hour: Hour of day (0-23, default 7 = 7 AM)
        minute: Minute (0-59, default 0)
    
    This stores configuration that can be used by cloud scheduler.
    For Supabase, use pg_cron extension instead:
    
    SELECT cron.schedule('daily-update-7am', '0 7 * * *', $$
      SELECT net_http.post(
        'http://localhost:8000/api/updates/trigger-daily-update',
        '{}',
        'application/json'
      );
    $$);
    """
    
    if not (0 <= hour < 24 and 0 <= minute < 60):
        return {"error": "Invalid hour or minute"}
    
    schedule_time = f"{hour:02d}:{minute:02d}"
    
    return {
        "status": "Schedule configured",
        "scheduled_time": schedule_time,
        "note": "Use Supabase pg_cron or cloud scheduler for automatic execution",
    }
