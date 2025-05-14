#!/usr/bin/env python3
import os
import sys
import json
import click
from pathlib import Path
from datetime import datetime
import logging
from rich.console import Console
from rich.table import Table
from rich import box
import subprocess
from appdirs import user_data_dir

# Add parent directory to path to import session_manager
sys.path.append(str(Path(__file__).parent))
from session_manager import (
    save_session, 
    load_session, 
    restore_session, 
    list_sessions, 
    delete_session, 
    get_session_summary
)

from config import get_current_workspace
import getpass

APP_NAME = "FleckCLI"
APP_AUTHOR = getpass.getuser() # Replace as needed

DATA_DIR = Path(user_data_dir(APP_NAME)+"/Data")
SESSIONS_DIR = DATA_DIR / "sessions"
TODO_FILE = DATA_DIR / "todos.json"
LOGS_DIR = DATA_DIR / "logs"

print(DATA_DIR)
print(SESSIONS_DIR)

os.makedirs(DATA_DIR,exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workspace_cli")

# Setup rich console
console = Console()

CURRENT_WORKSPACE = get_current_workspace()

@click.group()
def cli():
    """
    Workspace Manager CLI - Save and restore application workspaces.
    
    This tool helps you save your current workspace (applications and browser tabs)
    and restore them later, making task switching more efficient.
    """
    pass

@cli.command()
# @click.argument('task_name')
def save():
    """Save the current workspace for a specific task."""
    with console.status(f"Saving workspace for task '{CURRENT_WORKSPACE}'...", spinner="dots"):
        success, message = save_session(CURRENT_WORKSPACE)
    
    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        console.print(f"[red]✗[/red] {message}")

@cli.command()
@click.argument('task_name')
def restore(task_name):
    """Restore a saved workspace for a specific task."""
    # Check if session exists first
    session_data = load_session(task_name)
    if not session_data:
        console.print(f"[red]✗[/red] No saved workspace found for task: {task_name}")
        return
    
    # Show summary before restoring
    display_summary(task_name)
    
    if click.confirm(f"Do you want to restore the workspace for '{task_name}'?"):
        with console.status(f"Restoring workspace for task '{task_name}'...", spinner="dots"):
            success, message = restore_session(task_name)
        
        if success:
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[red]✗[/red] {message}")

import os
import psutil
import win32gui
import win32process

def get_gui_pids():
    """Get the PIDs of all top-level visible GUI windows."""
    gui_pids = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                gui_pids.add(pid)
            except Exception:
                pass
        return True

    win32gui.EnumWindows(callback, None)
    return gui_pids


def kill_only_gui_apps(exclude_names=None, dry_run=True):
    exclude_names = set(name.lower() for name in (exclude_names or []))
    gui_pids = get_gui_pids()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name'].lower()
            pid = proc.info['pid']

            if name in exclude_names or pid not in gui_pids:
                continue

            if dry_run:
                print(f"[Dry Run] Would kill GUI app: {name} (PID: {pid})")
            else:
                proc.kill()
                print(f"Killed GUI app: {name} (PID: {pid})")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


@click.command()
@click.argument('task_name')
def focus(task_name):
    """Enter Focus Mode: Close all apps and restore workspace for the given task."""
    session_data = load_session(task_name)
    if not session_data:
        console.print(f"[red]✗[/red] No saved workspace found for task: {task_name}")
        return

    display_summary(task_name)
    if click.confirm(f"Do you want to enter focus mode for '{task_name}'?"):
        # with console.status(f"[yellow]Closing apps and restoring workspace for '{task_name}'...[/yellow]", spinner="dots"):
            # Define processes to exclude (system critical + Python + this script)
            exclude = ['explorer.exe', 'python.exe', 'code.exe', 'cmd.exe', 'powershell.exe','brave.exe',"fleck.exe"]  # Add more if needed

            kill_only_gui_apps(exclude,False)
            print("works")
            switch_helper(task_name)
            # success, message = switch_helper(task_name)

            # if success:
            #     console.print(f"[green]✓[/green] {message}")
            # else:
            #     console.print(f"[red]✗[/red] {message}")

cli.add_command(focus, name="focus")
    
from enum import Enum
# Constants
# TODO_FILE = Path(__file__).parent / "data" / "todos.json"
TODO_FILE = Path(TODO_FILE)
PRIORITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
    None: "white"
}

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = None

class Status(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress" 
    PAUSED = "Paused"
    DONE = "Done"



def load_data():
    """Load todo data from file."""
    if not TODO_FILE.exists():
        return {"current_task": None, "tasks": {}}
    
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"current_task": None, "tasks": {}}

def save_data(data):
    """Save todo data to file."""
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@cli.command()
def tasks():
    """List all available tasks."""
    data = load_data()
    sessions = list_sessions()

    if not sessions:
        console.print("[yellow]No saved workspaces found.[/yellow]")
        return

    table = Table(title="Saved Workspaces", box=box.ROUNDED)
    table.add_column("ID")
    table.add_column("Task", style="cyan")
    table.add_column("Last Saved", style="green")
    table.add_column("Apps", justify="right")
    table.add_column("Chrome Tabs", justify="right")
    table.add_column("Brave Tabs", justify="right")
    table.add_column("Edge Tabs", justify="right")
    table.add_column("Folders", justify="right")
    table.add_column("Todo Count", justify="right")

    for task_data in sessions:
        task_name_raw = task_data["name"]
        if task_name_raw == "current_session":
            continue

        # Highlight current workspace
        task_name_display = (
            f"[bold green]{task_name_raw} (current)[/bold green]"
            if task_name_raw == CURRENT_WORKSPACE else task_name_raw
        )

        timestamp = "Unknown"
        if task_data.get("timestamp"):
            try:
                dt = datetime.fromisoformat(task_data["timestamp"])
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        todo_count = len(data["tasks"].get(task_name_raw, {}).get("todos", []))

        table.add_row(
            str(task_data.get("id", "-")),
            task_name_display,
            str(timestamp),
            str(task_data.get("app_count", 0)),
            str(task_data.get("chrome_tabs", 0)),
            str(task_data.get("brave_tabs", 0)),
            str(task_data.get("edge_tabs", 0)),
            str(task_data.get("explorer", 0)),
            str(todo_count)
        )

    console.print(table)


@cli.command()
@click.argument('description')
@click.option('--priority', type=click.Choice([p.value for p in Priority]), 
              default=Priority.NONE.value, help="Priority of the todo")
def add(description, priority):
    """Add a new todo to the current task."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    todo_id = str(len(data["tasks"][current_task]["todos"]) + 1)
    data["tasks"][current_task]["todos"][todo_id] = {
        "description": description,
        "status": Status.TODO.value,
        "priority": priority if priority != "None" else None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    console.print(f"[green]Added todo #{todo_id} to task '{current_task}'[/green]")


from fleck.timer_utils import start_timer, pause_timer
from fleck.timer_utils import stop_timer_and_get_elapsed
from fleck.timer_utils import get_timer_status, display_live_timer\

from fleck.git_support import git_push

# @cli.command()
# @click.argument('todo_id')
# def done(todo_id):
#     """Mark a todo as done."""
#     data = load_data()
#     current_task =  CURRENT_WORKSPACE
    
#     if not current_task:
#         console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
#         return
    
#     if todo_id not in data["tasks"][current_task]["todos"]:
#         console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
#         return
    
#     elapsed = stop_timer_and_get_elapsed(current_task, todo_id)
    
#     data["tasks"][current_task]["todos"][todo_id]["status"] = Status.DONE.value
#     data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
#     data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
#     data["tasks"][current_task]["todos"][todo_id]["time_spent"] = elapsed
#     save_data(data)
#     console.print(f"[green]Marked todo #{todo_id} as done. Total time: {format_seconds(elapsed)}[/green]")

@cli.command()
@click.argument('todo_id')
def done(todo_id):
    """Mark a todo as done."""
    data = load_data()
    current_task = CURRENT_WORKSPACE

    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return

    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return

    elapsed = stop_timer_and_get_elapsed(current_task, todo_id)

    todo = data["tasks"][current_task]["todos"][todo_id]
    todo["status"] = Status.DONE.value
    todo["updated_at"] = datetime.now().isoformat()
    todo["time_spent"] = elapsed
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()

    save_data(data)

    console.print(f"[green]✓ Marked todo #{todo_id} as done. Total time: {format_seconds(elapsed)}[/green]")

    # Ask user if they want to push
    if click.confirm("Do you want to git push this change?"):
        commit_msg = f"Mark todo '{todo['description']}' as done"
        git_push(todo['description'])



def format_seconds(seconds):
    """Format seconds into a readable time string."""
    from datetime import timedelta
    return str(timedelta(seconds=int(seconds)))

@cli.command()
@click.argument('todo_id')
@click.argument('priority', type=click.Choice([p.value for p in Priority]))
def flag(todo_id, priority):
    """Set priority for a todo."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    priority_value = priority if priority != "None" else None
    data["tasks"][current_task]["todos"][todo_id]["priority"] = priority_value
    data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    console.print(f"[green]Set priority for todo #{todo_id} to {priority_value or 'none'}[/green]")

@cli.command()
@click.argument('filter', required=False, type=click.Choice(["todo", "running", "paused", "done"]))
def list(filter):
    """List all todos for the current task with a TUI display."""
    data = load_data()
    current_task = CURRENT_WORKSPACE

    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return

    todos = data["tasks"][current_task]["todos"]
    if not todos:
        console.print(f"[yellow]No todos found in task '{current_task}'[/yellow]")
        return

    # Normalize filter value
    status_filter = None
    if filter == "todo":
        status_filter = "To Do"
    elif filter == "running":
        status_filter = "In Progress"
    elif filter == "paused":
        status_filter = "Paused"
    elif filter == "done":
        status_filter = "Done"

    table = Table(title=f"Todos for Task: {current_task}" + (f" (Filtered: {status_filter})" if status_filter else ""), box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Created At")
    table.add_column("Time")

    rowCnt = 0
    for todo_id, todo in sorted(todos.items(), key=lambda x: x[0]):
        priority = todo.get("priority")
        status = todo.get("status")
        
        # Get time info based on status
        if status == Status.DONE.value:
            time_str = format_seconds(todo.get("time_spent", 0))
            status_color = "green"
        elif status == Status.IN_PROGRESS.value:
            # Get current timer status
            timer_status = get_timer_status(current_task, todo_id)
            time_str = timer_status["formatted_time"] + " (running)"
            status_color = "yellow"
        elif status == Status.PAUSED.value:
            # Get paused timer status
            timer_status = get_timer_status(current_task, todo_id)
            time_str = timer_status["formatted_time"] + " (paused)"
            status_color = "blue"
        else:
            time_str = "-"
            status_color = "white"

        created_at = datetime.fromisoformat(todo["created_at"]).strftime("%Y-%m-%d %H:%M")

        if not status_filter or status == status_filter:
            table.add_row(
                todo_id,
                todo["description"],
                f"[{status_color}]{status}[/{status_color}]",
                f"[{PRIORITY_COLORS[priority]}]{priority or 'none'}[/{PRIORITY_COLORS[priority]}]",
                created_at,
                time_str
            )
            rowCnt += 1

    if rowCnt > 0:
        console.print(table)
    else:
        console.print(f"[green]No todos left with status '{status_filter}'[/green]")


@cli.command()
@click.argument('todo_id')
def gui_timer(todo_id):
    """Launch a GUI timer window for a todo."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    todo = data["tasks"][current_task]["todos"][todo_id]
    
    if todo["status"] == Status.DONE.value:
        console.print(f"[yellow]Todo #{todo_id} is already done. Cannot start timer.[/yellow]")
        return
        
    # If the todo is not in progress, mark it as in progress
    if todo["status"] != Status.IN_PROGRESS.value and todo["status"] != Status.PAUSED.value:
        data["tasks"][current_task]["todos"][todo_id]["status"] = Status.IN_PROGRESS.value
        data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
        data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
        save_data(data)
        start_timer(current_task, todo_id)
        console.print(f"[green]Marked todo #{todo_id} as in progress.[/green]")
    
    # Launch GUI timer
    import subprocess
    import sys
    from pathlib import Path
    
    script_path = Path(__file__).parent / "timer_gui.py"
    
    try:
        # Start the GUI timer in a separate process
        subprocess.Popen([sys.executable, str(script_path), current_task, todo_id], 
                        start_new_session=True)
        console.print(f"[green]Launched timer GUI for todo #{todo_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error launching timer GUI: {e}[/red]")


@cli.command()
@click.argument('todo_id')
@click.option('--gui', is_flag=True, help="Start the timer and show in a GUI window")
def progress(todo_id, gui):
    """Mark a todo as in progress and start the timer."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    data["tasks"][current_task]["todos"][todo_id]["status"] = Status.IN_PROGRESS.value
    data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    start_timer(current_task, todo_id)
    console.print(f"[green]Marked todo #{todo_id} as in progress. Timer started.[/green]")
    
    # If GUI flag is set, launch the GUI timer
    if gui:
        import subprocess
        import sys
        from pathlib import Path
        
        script_path = Path(__file__).parent / "timer_gui.py"
        
        try:
            # Start the GUI timer in a separate process
            subprocess.Popen([sys.executable, str(script_path), current_task, todo_id], 
                           start_new_session=True)
            console.print(f"[green]Launched timer GUI for todo #{todo_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error launching timer GUI: {e}[/red]")

@cli.command()
@click.argument('todo_id')
def pause(todo_id):
    """Pause a todo that's in progress."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    todo = data["tasks"][current_task]["todos"][todo_id]
    if todo["status"] != Status.IN_PROGRESS.value:
        console.print(f"[yellow]Todo #{todo_id} is not in progress. Cannot pause.[/yellow]")
        return
    
    # elapsed = pause_timer(current_task, todo_id)
    # pause_timer(current_task,todo_id)
    
    data["tasks"][current_task]["todos"][todo_id]["status"] = Status.PAUSED.value
    data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    console.print(f"[green]Paused todo #{todo_id}. Current elapsed time: {format_seconds(pause_timer(current_task,todo_id))}[/green]")

@cli.command()
@click.argument('todo_id')
def resume(todo_id):
    """Resume a paused todo."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    todo = data["tasks"][current_task]["todos"][todo_id]
    if todo["status"] != Status.PAUSED.value:
        console.print(f"[yellow]Todo #{todo_id} is not paused. Cannot resume.[/yellow]")
        return
    
    data["tasks"][current_task]["todos"][todo_id]["status"] = Status.IN_PROGRESS.value
    data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    start_timer(current_task, todo_id)
    console.print(f"[green]Resumed todo #{todo_id}. Timer started.[/green]")

@cli.command()
@click.argument('todo_id')
@click.option('--gui', is_flag=True, help="Show timer in a GUI window")
def timer(todo_id, gui):
    """Show a live timer for a todo that's in progress."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    todo = data["tasks"][current_task]["todos"][todo_id]
    status = get_timer_status(current_task, todo_id)
    
    if todo["status"] == Status.DONE.value:
        console.print(f"[yellow]Todo #{todo_id} is already done. Total time: {format_seconds(todo.get('time_spent', 0))}[/yellow]")
        return
    
    if todo["status"] == Status.TODO.value:
        # Automatically set to in progress if it's not started yet
        data["tasks"][current_task]["todos"][todo_id]["status"] = Status.IN_PROGRESS.value
        data["tasks"][current_task]["todos"][todo_id]["updated_at"] = datetime.now().isoformat()
        data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
        save_data(data)
        start_timer(current_task, todo_id)
        console.print(f"[green]Marked todo #{todo_id} as in progress.[/green]")
    
    if gui:
        # Launch GUI timer in a separate process
        import subprocess
        import sys
        from pathlib import Path
        
        script_path = Path(__file__).parent / "timer_gui.py"
        
        try:
            # Start the GUI timer in a separate process
            subprocess.Popen([sys.executable, str(script_path), current_task, todo_id], 
                           start_new_session=True)
            console.print(f"[green]Launched timer GUI for todo #{todo_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error launching timer GUI: {e}[/red]")
            # Fall back to console timer
            display_live_timer(current_task, todo_id)
    else:
        # Display live timer in the console
        display_live_timer(current_task, todo_id)

@cli.command()
@click.argument('todo_id')
def delete(todo_id):
    """Delete a todo from the current task."""
    data = load_data()
    current_task = CURRENT_WORKSPACE
    
    if not current_task:
        console.print("[red]No active task. Use 'start <task_name>' to begin.[/red]")
        return
    
    if todo_id not in data["tasks"][current_task]["todos"]:
        console.print(f"[red]Todo #{todo_id} not found in current task.[/red]")
        return
    
    # Stop any running timer for this todo
    stop_timer_and_get_elapsed(current_task, todo_id)
    
    del data["tasks"][current_task]["todos"][todo_id]
    data["tasks"][current_task]["updated_at"] = datetime.now().isoformat()
    save_data(data)
    console.print(f"[green]Deleted todo #{todo_id} from task '{current_task}'[/green]")








@cli.command()
def delete_workspace():
    """Delete a saved workspace."""
    global CURRENT_WORKSPACE
    # sessions_dir = Path(__file__).parent / "data" / "sessions"
    sessions_dir = SESSIONS_DIR
    current_file = sessions_dir / "current_session.json"
    # todos_file = Path("data") / "todos.json"
    todos_file = TODO_FILE

    if click.confirm(f"Are you sure you want to delete the workspace for '{CURRENT_WORKSPACE}'?"):
        success, message = delete_session(CURRENT_WORKSPACE)

        if success:
            # Clear current session
            with open(current_file, "w") as f:
                json.dump({"current": ""}, f)

            # Remove from todos.json
            if todos_file.exists():
                with open(todos_file, "r") as f:
                    todos_data = json.load(f)
                if CURRENT_WORKSPACE in todos_data.get("tasks", {}):
                    del todos_data["tasks"][CURRENT_WORKSPACE]
                    with open(todos_file, "w") as f:
                        json.dump(todos_data, f, indent=4)
                    console.print(f"[green]✓[/green] Removed '{CURRENT_WORKSPACE}' from todos.json")
                else:
                    console.print(f"[yellow]⚠[/yellow] Workspace not found in todos.json")

            # Reset the in-memory global variable
            CURRENT_WORKSPACE = ""

            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[red]✗[/red] {message}")


@cli.command()
# @click.argument('task_name')
def show():
    """Show details of a saved workspace."""
    display_summary(CURRENT_WORKSPACE)

@cli.command()
# @click.argument('task_name')
def gui():
    """Open the workspace in the GUI viewer."""
    # Check if the session exists
    session_data = load_session(CURRENT_WORKSPACE)
    if not session_data:
        console.print(f"[red]✗[/red] No saved workspace found for task: {CURRENT_WORKSPACE}")
        return
    
    # Get the path to the workspace_gui.py file
    workspace_gui_path = Path(__file__).parent / "workspace_gui.py"
    
    if not workspace_gui_path.exists():
        console.print(f"[red]✗[/red] Workspace GUI not found at: {workspace_gui_path}")
        return
    
    # Launch the GUI
    try:
        subprocess.Popen([sys.executable, str(workspace_gui_path), CURRENT_WORKSPACE])
        console.print(f"[green]✓[/green] Launched workspace viewer for '{CURRENT_WORKSPACE}'")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to launch workspace viewer: {e}")

def display_summary(task_name):
    """Display a summary of a workspace."""
    summary = get_session_summary(task_name)
    
    if not summary:
        console.print(f"[red]✗[/red] No saved workspace found for task: {task_name}")
        return
    
    # Format timestamp
    timestamp = "Unknown"
    if summary.get("timestamp"):
        try:
            dt = datetime.fromisoformat(summary["timestamp"])
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    
    # Print summary header
    console.print(f"\n[bold cyan]Workspace Summary for '{task_name}'[/bold cyan]")
    console.print(f"[dim]Last saved: {timestamp}[/dim]\n")
    
    # Applications table
    if summary["applications"]:
        app_table = Table(title="Applications", box=box.SIMPLE)
        app_table.add_column("Name", style="green")
        app_table.add_column("Window Title")
        
        for app in summary["applications"]:
            app_table.add_row(app["name"], app["title"])
        
        console.print(app_table)
    else:
        console.print("[yellow]No applications saved in this workspace.[/yellow]")
    
    # Chrome tabs table
    if summary["chrome_tabs"]:
        chrome_table = Table(title="Chrome Tabs", box=box.SIMPLE)
        chrome_table.add_column("Title", style="blue")
        # chrome_table.add_column("URL", style="cyan")
        
        for tab in summary["chrome_tabs"]:
            url = tab["url"] or ""
            title = tab["title"] or "No Title"
            # chrome_table.add_row(f"[link={url}]{title}[/link]", url)
            chrome_table.add_row(f"[link={url}]{title}[/link]")
        
        console.print(chrome_table)
    
    # Brave tabs table
    if summary["brave_tabs"]:
        brave_table = Table(title="Brave Tabs", box=box.SIMPLE)
        brave_table.add_column("Title", style="orange1")
        # brave_table.add_column("URL", style="cyan")
        
        for tab in summary["brave_tabs"]:
            url = tab["url"] or ""
            title = tab["title"] or "No Title"
            # brave_table.add_row(f"[link={url}]{title}[/link]", url)
            brave_table.add_row(f"[link={url}]{title}[/link]")
        
        console.print(brave_table)
    else:
        console.print("[yellow]No Brave tabs saved in this workspace.[/yellow]")
    
    console.print("")
    
    if summary["edge_tabs"]:
        edge_table = Table(title="Edge Tabs", box=box.SIMPLE)
        edge_table.add_column("Title", style="orange1")
        # edge_table.add_column("URL", style="cyan")
        
        for tab in summary["edge_tabs"]:
            url = tab["url"] or ""
            title = tab["title"] or "No Title"
            # edge_table.add_row(f"[link={url}]{title}[/link]", url)
            edge_table.add_row(f"[link=${url}]{title}[/link]")
        
        console.print(edge_table)
    else:
        console.print("[yellow]No Edge tabs saved in this workspace.[/yellow]")
    
    console.print("")

    if summary["explorer"]:
        explorer_table = Table(title="File Explorer",box=box.SIMPLE)
        explorer_table.add_column("Folder",style="magenta")
        explorer_table.add_column("Path",style="cyan")

        for tab in summary["explorer"]:
            path = tab["path"]
            title = tab["title"]
            explorer_table.add_row(title,path)
        console.print(explorer_table)
    else:
        console.print("[yellow]No files saved in this workspace.[/yellow]")
    
    console.print("")  # Add a blank line at the end

from session_tracker import start_session_tracking
from workspace_manager import restore_workspace_state
import time


@cli.command()
# @click.argument('task_name')
def track_session():
    """Start session tracking (app + browser tab) with auto-browser launch"""
    click.echo("🚀 Starting session tracking...")
    start_session_tracking(CURRENT_WORKSPACE)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("🛑 Session tracking stopped.")


@cli.command()
@click.argument('workspace_name')
def create(workspace_name):
    """Create a new workspace"""
    # os.makedirs('data/sessions', exist_ok=True)
    # session_path = os.path.join('data/sessions', f"{workspace_name}.json")
    session_path = os.path.join(SESSIONS_DIR,f"{workspace_name}.json")

    if os.path.exists(session_path):
        click.echo(f"Workspace '{workspace_name}' already exists.")
        return

    # Create initial session file
    initial_data = {
        "timestamp": "",
        "applications": [],
        "explorer": [],
        "chrome_tabs": [],
        "brave_tabs": [],
        "edge_tabs": []
    }
    with open(session_path, 'w') as f:
        json.dump(initial_data, f, indent=4)

    # Update todos.json
    # todos_path = Path("data") / "todos.json"
    todos_path = TODO_FILE
    if todos_path.exists():
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
    else:
        todos_data = {"tasks": {}}

    if workspace_name in todos_data["tasks"]:
        console.print(f"[yellow]Warning: Task '{workspace_name}' already exists in todos.json[/yellow]")
    else:
        now = datetime.now().isoformat()
        todos_data["tasks"][workspace_name] = {
            "id":len(todos_data["tasks"])+1,
            "created_at": now,
            "updated_at": now,
            "todos": {}
        }
        with open(todos_path, "w") as f:
            json.dump(todos_data, f, indent=4)
        console.print(f"[green]✓[/green] Added '{workspace_name}' to todos.json")

    click.echo(f"Workspace '{workspace_name}' created.")

    # ✅ Update current workspace (persist it)
    current_path = Path(f"{SESSIONS_DIR}/current_session.json")
    with open(current_path, "w") as f:
        json.dump({"current": workspace_name}, f)



@cli.command()
def current():
    """Show the currently active workspace."""
    # curr_file = Path(__file__).parent / "data" / "sessions" / "current_session.json"
    curr_file = Path(f"{SESSIONS_DIR}/current_session.json")

    if not curr_file.exists():
        console.print("[yellow]No current active file[/yellow]")
        return

    with open(curr_file, "r") as f:
        data = json.load(f)

    curr = data.get("current", "")
    if curr == "":
        console.print("[yellow]No current active workspace[/yellow]")
    else:
        console.print(f"[green]{curr} is active[/green]")

def switch_helper(workspace_name):
    # sessions_dir = Path(__file__).parent / "data" / "sessions"
    sessions_dir = SESSIONS_DIR
    session_path = sessions_dir / f"{workspace_name}.json"
    current_file = sessions_dir / "current_session.json"

    if not session_path.exists():
        console.print(f"[red]✗ Workspace '{workspace_name}' does not exist.[/red]")
        return

    # Save current session if exists and confirmed
    if current_file.exists():
        with open(current_file, "r") as f:
            current_data = json.load(f)
        current_workspace = current_data.get("current", "")

        # if current_workspace and current_workspace != workspace_name:
        if click.confirm(f"Do you want to save the current workspace '{CURRENT_WORKSPACE}' before switching?"):
                success, msg = save_session(CURRENT_WORKSPACE)  # Assuming this returns (bool, str)
                if success:
                    console.print(f"[green]✓[/green] {msg}")
                else:
                    console.print(f"[red]✗[/red] Failed to save: {msg}")

    # Set new current workspace
    with open(current_file, "w") as f:
        json.dump({"current": workspace_name}, f)
    console.print(f"[blue]→ Switched to workspace:[/blue] '{workspace_name}'")

    # Display and optionally restore
    display_summary(workspace_name)
    if click.confirm(f"Do you want to restore the workspace for '{workspace_name}'?"):
        with console.status(f"Restoring workspace '{workspace_name}'...", spinner="dots"):
            success, message = restore_session(workspace_name)
        if success:
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[red]✗[/red] {message}")
    else:
        console.print(f"[yellow]⚠ Workspace switched but not restored.[/yellow]")



@cli.command()
@click.argument("workspace_name")
def switch(workspace_name):
    """Switch to another workspace and restore its session."""
    # sessions_dir = Path(__file__).parent / "data" / "sessions"
    sessions_dir = SESSIONS_DIR
    session_path = sessions_dir / f"{workspace_name}.json"
    current_file = sessions_dir / "current_session.json"

    if not session_path.exists():
        console.print(f"[red]✗ Workspace '{workspace_name}' does not exist.[/red]")
        return

    # Save current session if exists and confirmed
    if current_file.exists():
        with open(current_file, "r") as f:
            current_data = json.load(f)
        current_workspace = current_data.get("current", "")

        # if current_workspace and current_workspace != workspace_name:
        if click.confirm(f"Do you want to save the current workspace '{CURRENT_WORKSPACE}' before switching?"):
                success, msg = save_session(CURRENT_WORKSPACE)  # Assuming this returns (bool, str)
                if success:
                    console.print(f"[green]✓[/green] {msg}")
                else:
                    console.print(f"[red]✗[/red] Failed to save: {msg}")

    # Set new current workspace
    with open(current_file, "w") as f:
        json.dump({"current": workspace_name}, f)
    console.print(f"[blue]→ Switched to workspace:[/blue] '{workspace_name}'")

    # Display and optionally restore
    display_summary(workspace_name)
    if click.confirm(f"Do you want to restore the workspace for '{workspace_name}'?"):
        with console.status(f"Restoring workspace '{workspace_name}'...", spinner="dots"):
            success, message = restore_session(workspace_name)
        if success:
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[red]✗[/red] {message}")
    else:
        console.print(f"[yellow]⚠ Workspace switched but not restored.[/yellow]")







# cli.py
# import click
# import os
# from session_tracker import start_session_tracking
# from workspace_manager import restore_workspace_state

# tracking_threads = {}

# @click.group()
# def cli():
#     """Workspace session manager CLI"""
#     pass



# @cli.command()
# @click.argument('workspace_name')
# def start(workspace_name):
#     """Start tracking a workspace"""
#     path = os.path.join('workspaces', workspace_name)
#     if not os.path.exists(path):
#         click.echo(f"Workspace '{workspace_name}' does not exist.")
#         return

#     click.echo(f"Starting session tracking for '{workspace_name}'...")
#     base_path = os.path.join(path, workspace_name)
#     thread = start_session_tracking(base_path)
#     tracking_threads[workspace_name] = thread

# @cli.command()
# @click.argument('workspace_name')
# def restore(workspace_name):
#     """Restore the state of a workspace"""
#     path = os.path.join('workspaces', workspace_name)
#     if not os.path.exists(path):
#         click.echo(f"Workspace '{workspace_name}' does not exist.")
#         return
#     click.echo(f"Restoring workspace '{workspace_name}'...")
#     base_path = os.path.join(path, workspace_name)
#     restore_workspace_state(base_path)

# @cli.command()
# def list():
#     """List all workspaces"""
#     if not os.path.exists('workspaces'):
#         click.echo("No workspaces found.")
#         return
#     workspaces = os.listdir('workspaces')
#     for w in workspaces:
#         click.echo(w)

# @cli.command()
# @click.argument('workspace_name')
# def switch(workspace_name):
#     """Switch to another workspace"""
#     click.echo(f"Switching to workspace '{workspace_name}'...")
#     restore(workspace_name)
#     start(workspace_name)

if __name__ == '__main__':
    cli()
