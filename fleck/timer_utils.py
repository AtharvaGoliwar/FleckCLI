import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import threading
import signal
import sys

# Constants
TIMER_FILE = Path(__file__).parent / "data" / "timers.json"

def ensure_timer_file():
    """Ensure the timer file exists."""
    os.makedirs(TIMER_FILE.parent, exist_ok=True)
    if not TIMER_FILE.exists():
        with open(TIMER_FILE, 'w') as f:
            json.dump({}, f)

def load_timer_data():
    """Load timer data from file."""
    ensure_timer_file()
    try:
        with open(TIMER_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_timer_data(data):
    """Save timer data to file."""
    ensure_timer_file()
    with open(TIMER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def start_timer(task_name, todo_id):
    """Start a timer for a specific todo item."""
    timer_data = load_timer_data()
    
    # Create timer key
    timer_key = f"{task_name}:{todo_id}"
    
    # Initialize or update timer data
    if timer_key not in timer_data:
        timer_data[timer_key] = {
            "start_time": time.time(),
            "elapsed": 0,
            "is_running": True,
            "paused_at": None
        }
    else:
        # Resume timer if it was paused
        if not timer_data[timer_key]["is_running"]:
            paused_elapsed = timer_data[timer_key]["elapsed"]
            timer_data[timer_key] = {
                "start_time": time.time(),
                "elapsed": paused_elapsed,
                "is_running": True,
                "paused_at": None
            }
    
    save_timer_data(timer_data)

def pause_timer(task_name, todo_id):
    """Pause a timer for a specific todo item."""
    timer_data = load_timer_data()
    timer_key = f"{task_name}:{todo_id}"
    timer_data[timer_key]["is_running"] = False
    # print(timer_data[timer_key]["is_running"])
    if (timer_key in timer_data) and (not timer_data[timer_key]["is_running"]):
        # Calculate elapsed time so far
        current_time = time.time()
        start_time = timer_data[timer_key]["start_time"]
        previous_elapsed = timer_data[timer_key]["elapsed"]
        
        # Update timer data
        timer_data[timer_key]["elapsed"] = previous_elapsed + (current_time - start_time)
        timer_data[timer_key]["paused_at"] = current_time
        
        save_timer_data(timer_data)
        # print()
        return timer_data[timer_key]["elapsed"]
    
    return 0

def stop_timer_and_get_elapsed(task_name, todo_id):
    """Stop a timer and return the total elapsed time."""
    elapsed = pause_timer(task_name, todo_id)

    
    # Remove the timer data for this todo
    timer_data = load_timer_data()
    timer_key = f"{task_name}:{todo_id}"
    
    if timer_key in timer_data:
        abc = timer_data[timer_key]["elapsed"]
        print(abc)
        del timer_data[timer_key]
        save_timer_data(timer_data)
        return abc
    
    return elapsed

def get_timer_status(task_name, todo_id):
    """Get the current status of a timer."""
    timer_data = load_timer_data()
    timer_key = f"{task_name}:{todo_id}"
    
    if timer_key not in timer_data:
        return {
            "is_running": False,
            "elapsed": 0,
            "formatted_time": "00:00:00"
        }
    
    timer_info = timer_data[timer_key]
    
    if timer_info["is_running"]:
        # Calculate current elapsed time
        current_elapsed = timer_info["elapsed"] + (time.time() - timer_info["start_time"])
    else:
        current_elapsed = timer_info["elapsed"]
    
    # Format time as HH:MM:SS
    formatted_time = str(timedelta(seconds=int(current_elapsed)))
    
    return {
        "is_running": timer_info["is_running"],
        "elapsed": current_elapsed,
        "formatted_time": formatted_time
    }

def display_live_timer(task_name, todo_id):
    """Display a live timer for a todo item."""
    # Setup to handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nTimer stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"Timer for task '{task_name}', todo #{todo_id}")
    print("Press Ctrl+C to exit the timer view")
    
    try:
        while True:
            status = get_timer_status(task_name, todo_id)
            
            if not status["is_running"]:
                print(f"\rTimer paused: {status['formatted_time']}", end="")
                time.sleep(1)
                continue
                
            print(f"\rElapsed time: {status['formatted_time']}", end="")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting timer view.")