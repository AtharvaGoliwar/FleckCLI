import tkinter as tk
import time
import threading
import json
import os
from pathlib import Path
import subprocess
import sys

from fleck.timer_utils import stop_timer_and_get_elapsed

# Constants
TIMER_FILE = Path(__file__).parent / "data" / "timers.json"
TODO_FILE = Path(__file__).parent / "data" / "todos.json"

class TimerApp:
    def __init__(self, root, task_name, todo_id, description):
        self.root = root
        self.task_name = task_name
        self.todo_id = todo_id
        self.description = description
        self.timer_key = f"{task_name}:{todo_id}"
        self.is_running = False
        self.elapsed_time = 0
        self.update_thread = None
        self.should_stop = False

        # Window setup
        self.root.title(f"Timer - {task_name}: Todo #{todo_id}")
        self.root.geometry("350x200")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.attributes("-topmost", True)  # Keep window on top
        
        # Set a nice background color
        self.root.configure(bg="#f0f0f0")
        
        # Task description
        tk.Label(root, text=f"Task: {task_name}", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(10, 0))
        tk.Label(root, text=f"Todo #{todo_id}: {description}", font=("Arial", 10), bg="#f0f0f0", wraplength=300).pack(pady=(5, 10))
        
        # Timer display
        self.time_display = tk.Label(root, text="00:00:00", font=("Arial", 24), bg="#f0f0f0")
        self.time_display.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        # Pause/Resume button
        self.pause_button = tk.Button(button_frame, text="Pause", command=self.toggle_pause, width=10, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.pause_button.grid(row=0, column=0, padx=5)
        
        # Mark as Done button
        self.done_button = tk.Button(button_frame, text="Mark Done", command=self.mark_as_done, width=10, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.done_button.grid(row=0, column=1, padx=5)
        
        # Load timer data
        self.load_timer_data()
        
        # Start the timer update
        self.update_timer()

    def load_timer_data(self):
        """Load timer data from file"""
        try:
            if TIMER_FILE.exists():
                with open(TIMER_FILE, 'r') as f:
                    timer_data = json.load(f)
                    
                if self.timer_key in timer_data:
                    timer_info = timer_data[self.timer_key]
                    self.is_running = timer_info.get("is_running", False)
                    
                    if self.is_running:
                        # Calculate current elapsed time
                        self.elapsed_time = timer_info.get("elapsed", 0) + (time.time() - timer_info.get("start_time", time.time()))
                    else:
                        self.elapsed_time = timer_info.get("elapsed", 0)
                        
                    # Update button text based on state
                    if self.is_running:
                        self.pause_button.config(text="Pause", bg="#ff9800")
                    else:
                        self.pause_button.config(text="Resume", bg="#4CAF50")
        except Exception as e:
            print(f"Error loading timer data: {e}")
            self.elapsed_time = 0
            self.is_running = False

    def update_timer(self):
        """Update the timer display"""
        if not self.should_stop:
            if self.is_running:
                self.elapsed_time += 0.1
            
            # Format time as HH:MM:SS
            hours, remainder = divmod(int(self.elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.time_display.config(text=time_str)
            
            # Schedule the next update
            self.root.after(100, self.update_timer)

    def toggle_pause(self):
        """Toggle between pause and resume"""
        if self.is_running:
            self.pause_timer()
            self.pause_button.config(text="Resume", bg="#4CAF50")
        else:
            self.resume_timer()
            self.pause_button.config(text="Pause", bg="#ff9800")

    def pause_timer(self):
        """Pause the timer"""
        self.is_running = False
        self.save_timer_state()
        
        # Run CLI command to update task status
        # subprocess.run([sys.executable, "-m", "fleck.cli", "pause", self.todo_id])
        subprocess.run(["fleck","pause",str(self.todo_id)])

    def resume_timer(self):
        """Resume the timer"""
        self.is_running = True
        self.save_timer_state()
        
        # Run CLI command to update task status
        # subprocess.run([sys.executable, "-m", "fleck.cli", "resume", self.todo_id])
        subprocess.run(["fleck","resume",str(self.todo_id)])

    def mark_as_done(self):
        """Mark the todo as done"""
        self.is_running = False
        self.save_timer_state()
        
        # Run CLI command to update task status
        # subprocess.run([sys.executable, "-m", "fleck.cli", "done", self.todo_id])
        subprocess.run(["fleck", "done", str(self.todo_id)])

        # stop_timer_and_get_elapsed(self.task_name,self.todo_id)
        
        # Close the window
        self.on_close()

    def save_timer_state(self):
        """Save timer state to file"""
        try:
            # Ensure directory exists
            os.makedirs(TIMER_FILE.parent, exist_ok=True)
            
            # Load existing data
            timer_data = {}
            if TIMER_FILE.exists():
                with open(TIMER_FILE, 'r') as f:
                    try:
                        timer_data = json.load(f)
                    except json.JSONDecodeError:
                        timer_data = {}
            
            # Update or create entry for this timer
            if self.is_running:
                timer_data[self.timer_key] = {
                    "start_time": time.time(),
                    "elapsed": self.elapsed_time,
                    "is_running": True,
                    "paused_at": None
                }
            else:
                timer_data[self.timer_key] = {
                    "start_time": time.time(),
                    "elapsed": self.elapsed_time,
                    "is_running": False,
                    "paused_at": time.time()
                }
            
            # Save to file
            with open(TIMER_FILE, 'w') as f:
                json.dump(timer_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving timer data: {e}")

    def on_close(self):
        """Handle window close event"""
        self.should_stop = True
        self.save_timer_state()
        self.root.destroy()

def get_todo_description(task_name, todo_id):
    """Get the description of a todo item"""
    try:
        if TODO_FILE.exists():
            with open(TODO_FILE, 'r') as f:
                data = json.load(f)
                
            if task_name in data["tasks"] and todo_id in data["tasks"][task_name]["todos"]:
                return data["tasks"][task_name]["todos"][todo_id].get("description", "No description")
    except Exception as e:
        print(f"Error getting todo description: {e}")
    
    return "Unknown todo"

def main():
    if len(sys.argv) < 3:
        print("Usage: python timer_gui.py <task_name> <todo_id>")
        return
    
    task_name = sys.argv[1]
    todo_id = sys.argv[2]
    
    # Get todo description
    description = get_todo_description(task_name, todo_id)
    
    # Create and run the GUI
    root = tk.Tk()
    app = TimerApp(root, task_name, todo_id, description)
    root.mainloop()

if __name__ == "__main__":
    main()