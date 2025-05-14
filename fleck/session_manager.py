import os
import json
import subprocess
import platform
import psutil
from pathlib import Path
from datetime import datetime
import logging
import getpass
from appdirs import user_data_dir
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_manager")

# Constants
# SESSION_DIR = Path(__file__).parent / "data" / "sessions"

os_name = platform.system()

APP_NAME = "FleckCLI"
APP_AUTHOR = getpass.getuser() # Replace as needed

DATA_DIR = Path(user_data_dir(APP_NAME)+"/Data")
SESSIONS_DIR = DATA_DIR / "sessions"

def ensure_sessions_directory():
    """Ensure the sessions directory exists."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_session_file(task_name):
    """Get the session file path for a task."""
    ensure_sessions_directory()
    return SESSIONS_DIR / f"{task_name}.json"

import win32com.client
def get_open_explorer_paths():
    """Return a list of dictionaries with title and path of open File Explorer folders."""
    paths = []
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        for window in shell.Windows():
            if window and window.FullName and "explorer.exe" in window.FullName.lower():
                folder = window.Document.Folder
                if folder and folder.Self:
                    folder_path = folder.Self.Path
                    if folder_path and os.path.exists(folder_path):
                        title = os.path.basename(folder_path) or folder_path
                        paths.append({
                            "title": title,
                            "path": folder_path
                        })
    except Exception as e:
        logger.warning(f"Failed to get Explorer folder paths: {e}")
    return paths

def restore_explorer_windows(paths):
    """Reopen Explorer windows to the given folder paths."""
    for path in paths:
        if os.path.exists(path["path"]):
            subprocess.Popen(f'explorer "{path["path"]}"')
            print("hello")


#def get_running_applications():
    """Get a list of running applications including File Explorer with folder paths."""
    """   excluded_paths = [
        "C:\\Windows\\SystemApps",
        "C:\\Windows\\ImmersiveControlPanel",
        "C:\\Windows\\WinSxS"
    ]
    excluded_names = {
        "TextInputHost",
        "ShellExperienceHost",
        "StartMenuExperienceHost",
        "ApplicationFrameHost",
        "RuntimeBroker",
        "SearchUI",
        "dllhost",
        "sihost",
        # explorer is included
    }

    system_apps = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "control panel": "control.exe",
            "task manager": "taskmgr.exe",
            "regedit": "regedit.exe",
            "charmap": "charmap.exe",
            "wordpad": "write.exe",
            "snipping tool": "snippingtool.exe",
            "clock": "explorer.exe shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App",
            "photos": "explorer.exe shell:AppsFolder\\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
            "settings": "ms-settings:",
            "store": "ms-windows-store:",
            "edge": "msedge.exe",
        }

    apps = []

    try:
        if os_name == "Windows":
            cmd = (
                "powershell \"Get-Process | Where-Object { $_.MainWindowTitle -ne '' } "
                "| Select-Object ProcessName, MainWindowTitle, Path | ConvertTo-Json\""
            )
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            data = json.loads(output)

            if isinstance(data, dict):
                data = [data]

            explorer_paths = get_open_explorer_paths()
            explorer_index = 0

            for process in data:
                name = process.get("ProcessName")
                path = process.get("Path")
                title = process.get("MainWindowTitle")

                if not name or not title or not path:
                    continue

                if name in excluded_names:
                    continue

                if any(path.lower().startswith(p.lower()) for p in excluded_paths):
                    continue

                # Add folder path if it's an explorer window
                if name.lower() == "explorer":
                    folder = explorer_paths[explorer_index] if explorer_index < len(explorer_paths) else os.path.expanduser("~\\Documents")
                    explorer_index += 1
                    apps.append({
                        "name": name,
                        "title": title,
                        "path": path,
                        "folder": folder
                    })
                else:
                    if name.lower() in system_apps:
                        apps.append({
                            "name": name,
                            "title": title,
                            "path": system_apps[name.lower()]
                        })
                    else:
                        apps.append({
                            "name": name,
                            "title": title,
                            "path": path
                        })

    except Exception as e:
        logger.error(f"Error getting running applications: {e}")

    return apps"""

def get_running_applications():
    """Get a list of running applications based on the operating system."""
    system_apps = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "control panel": "control.exe",
            "task manager": "taskmgr.exe",
            "regedit": "regedit.exe",
            "charmap": "charmap.exe",
            "wordpad": "write.exe",
            "snipping tool": "snippingtool.exe",
            "clock": "explorer.exe shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App",
            "photos": "explorer.exe shell:AppsFolder\\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
            "settings": "ms-settings:",
            "store": "ms-windows-store:",
            "edge": "msedge.exe",
        }
    apps = []

    try:
        if os_name == "Windows":
            # Use powershell to get running applications
            cmd = "powershell \"Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object ProcessName, MainWindowTitle, Path | ConvertTo-Json\""
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            data = json.loads(output)
            
            # Handle single process case where JSON doesn't return a list
            if isinstance(data, dict):
                data = [data]
                
            for process in data:
                if process.get("MainWindowTitle"):  # Only include processes with window titles
                    if(process.get("MainWindowTitle").lower() in system_apps):
                        apps.append({
                            "name": process.get("ProcessName"),
                            "title": process.get("MainWindowTitle"),
                            "path": system_apps[process.get("MainWindowTitle").lower()],
                        })    
                    else:
                        apps.append({
                            "name": process.get("ProcessName"),
                            "title": process.get("MainWindowTitle"),
                            "path": process.get("Path"),
                        })          
                # apps.append({
                #     "name":process.get("ProcessName"),
                #     "title": process.get("MainWindowTitle"),
                #     "path": process.get("Path")
                # })  
        
    except Exception as e:
        logger.error(f"Error getting running applications: {e}")
    
    return apps

import os
import json
import base64
import sqlite3
from pathlib import Path

def get_chrome_tabs_windows(task_name,browser="chrome"):
    """Retrieve open tabs from Chrome or Brave on Windows."""
    tabs = []
    session_file = get_session_file(task_name)
    if not os.path.exists(session_file):
        return []

    with open(session_file, "r") as f:
        try:
            target_session = json.load(f)
        except json.JSONDecodeError:
            return []
    
    print(browser)
    apps = target_session.get("applications", [])
    if not isinstance(apps, list) or not any(app.get("name") == browser for app in apps):
        return []

    local_appdata = os.getenv("LOCALAPPDATA")
    
    browser_map = {
        "chrome": os.path.join(local_appdata, "Google", "Chrome", "User Data", "Default"),
        "brave": os.path.join(local_appdata, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "msedge": os.path.join(local_appdata, "Microsoft", "Edge", "User Data", "Default")
    }
    
    profile_path = browser_map.get(browser.lower())
    if not profile_path or not os.path.exists(profile_path):
        return tabs

    try:
        history_db = os.path.join(profile_path, "History")
        if not os.path.exists(history_db):
            return tabs

        # Copy the database to avoid lock issues
        tmp_copy = history_db + ".copy"
        with open(history_db, 'rb') as src, open(tmp_copy, 'wb') as dst:
            dst.write(src.read())

        conn = sqlite3.connect(tmp_copy)
        cursor = conn.cursor()



        # Get URLs from history (most recent ones)
        cursor.execute("""
            SELECT DISTINCT urls.url, urls.title,urls.last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 20
        """)

        for url, title, timestamp in cursor.fetchall():
            tabs.append({
                "title": title,
                "url": url,
                "browser": browser,
                "timestamp":timestamp
            })

        conn.close()
        os.remove(tmp_copy)
    except Exception as e:
        logger.error(f"Error reading {browser} tabs from history DB: {e}")
    
    tabs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    # Remove duplicates (keep first occurrence which is the most recent)
    unique_urls = set()
    unique_tabs = []
    
    for tab in tabs:
        if tab["title"] not in unique_urls:
            unique_urls.add(tab["title"])
            unique_tabs.append(tab)
    
    print(unique_tabs)
    return unique_tabs


def save_session(task_name):
    """Save the current session state for a task."""
    try:
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "applications": get_running_applications(),
            "explorer":get_open_explorer_paths(),
            "chrome_tabs": get_chrome_tabs_windows(task_name,"chrome"),
            "brave_tabs": get_chrome_tabs_windows(task_name,"brave"),
            "edge_tabs": get_chrome_tabs_windows(task_name,"msedge"),
            # "brave_tabs":[]
        }

        print(get_open_explorer_paths())
        
        session_file = get_session_file(task_name)
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return True, f"Session saved for task: {task_name}"
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return False, f"Failed to save session: {e}"

def load_session(task_name):
    """Load and return the session data for a task."""
    session_file = get_session_file(task_name)
    if not session_file.exists():
        return None
    
    try:
        with open(session_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading session: {e}")
        return None

def open_application(app_info):
    """Open an application based on path or name."""
    try:
        if not app_info.get("path"):
            logger.warning(f"No path for application: {app_info.get('name')}")
            return False
        
        if os_name == "Windows":
            subprocess.Popen([app_info["path"]], shell=True)
        elif os_name == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", app_info["name"]])
        elif os_name == "Linux":
            subprocess.Popen([app_info["path"]])
        
        return True
    except Exception as e:
        logger.error(f"Error opening application {app_info.get('name')}: {e}")
        return False

def open_browser_tabs(tabs, browser="chrome"):
    """Open a list of browser tabs."""
    if not tabs:
        return True
    
    try:
        # Map browser names to commands
        browser_commands = {
            "chrome": {
                "Windows": "start chrome",
                "Darwin": "open -a \"Google Chrome\"",
                "Linux": "google-chrome"
            },
            "brave": {
                "Windows": "start brave",
                "Darwin": "open -a \"Brave Browser\"",
                "Linux": "brave-browser"
            },
            "msedge": {
                "Windows": "start msedge",
                "Darwin": "open -a \"Microsoft Edge\"",
                "Linux": "microsoft-edge"
            }
        }
        
        base_command = browser_commands.get(browser, {}).get(os_name)
        if not base_command:
            logger.warning(f"Unsupported browser {browser} on {os_name}")
            return False
        
        # Group URLs to open
        urls = [tab.get("url") for tab in tabs if tab.get("url")]
        if not urls:
            return True
        
        # Open all URLs at once
        if os_name == "Windows":
            url_args = " ".join([f'"{url}"' for url in urls])
            full_command = f"{base_command} {url_args}"
            subprocess.Popen(full_command, shell=True)
        elif os_name == "Darwin":
            # On macOS, we first open the browser then the URLs
            subprocess.Popen(base_command.split())
            for url in urls:
                subprocess.Popen([base_command, url], shell=True)
        elif os_name == "Linux":
            subprocess.Popen([base_command] + urls)
        
        return True
    except Exception as e:
        logger.error(f"Error opening browser tabs: {e}")
        return False

def restore_session(task_name):
    """Restore a saved session for a task."""
    session_data = load_session(task_name)
    if not session_data:
        return False, f"No saved session found for task: {task_name}"

    try:
        # Get currently running applications (by full path)
        running_apps = get_running_applications()
        running_paths = {app["path"].lower() for app in running_apps if "path" in app}

        # Open applications only if not already running
        for app in session_data.get("applications", []):
            app_path = app.get("path")
            if not app_path:
                continue
            if app_path.lower() in running_paths:
                logger.info(f"Skipping already running app: {app_path}")
                continue
            print("browser",app)
            open_application(app)
            if(app["name"]=="chrome"):
                open_browser_tabs(session_data.get("chrome_tabs", []), "chrome")
            elif(app["name"]=="brave"):
                open_browser_tabs(session_data.get("brave_tabs", []), "brave")
            elif app["name"]=="msedge":
                open_browser_tabs(session_data.get("edge_tabs",[]),"msedge")



        # Open Chrome tabs

        # Open Brave tabs
       

        

        import win32gui

        def is_folder_open(target_path):
            # Normalize and extract folder name
            target_folder = os.path.basename(os.path.normpath(target_path)).lower()

            def enum_window_callback(hwnd, open_folders):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and target_folder in title.lower():
                        open_folders.append(title)

            open_folders = []
            win32gui.EnumWindows(enum_window_callback, open_folders)
            return len(open_folders) > 0


        to_open_paths=[]

        for path in session_data.get("explorer",[]):
            target_path = path["path"]
            print("helloabc",path["path"])
            print(is_folder_open(target_path))
            if not target_path:
                continue
            if is_folder_open(target_path):
                logger.info(f"Skipping already running explorer path: {target_path}")
                continue
            to_open_paths.append(path)




        # restore_explorer_windows(session_data.get("explorer",[]))
        print("hello",to_open_paths)
        restore_explorer_windows(to_open_paths)

        return True, f"Session restored for task: {task_name}"
    except Exception as e:
        logger.error(f"Error restoring session: {e}")
        return False, f"Failed to restore session: {e}"
    



import psutil
import win32gui
import win32process

def is_gui_process(pid):
    """Check if a process has a visible window."""
    def callback(hwnd, gui_pids):
        if win32gui.IsWindowVisible(hwnd):
            try:
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                gui_pids.add(found_pid)
            except:
                pass
    gui_pids = set()
    win32gui.EnumWindows(callback, gui_pids)
    return pid in gui_pids

def kill_all_gui_apps(exclude_names=None):
    if exclude_names is None:
        exclude_names = ["explorer.exe", "python.exe", "code.exe"]  # Adjust this list

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if pname not in [e.lower() for e in exclude_names] and is_gui_process(proc.pid):
                print(f"Killing: {pname} (PID: {proc.pid})")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# Example usage
# kill_all_gui_apps()





def list_sessions():
    """List all saved sessions."""
    ensure_sessions_directory()
    sessions = []
    cnt=0
    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            with open(session_file, 'r') as f:
                cnt+=1
                data = json.load(f)
                sessions.append({
                    "name": session_file.stem,
                    "timestamp": data.get("timestamp"),
                    "app_count": len(data.get("applications", [])),
                    "chrome_tabs": len(data.get("chrome_tabs", [])),
                    "brave_tabs": len(data.get("brave_tabs", [])),
                    "edge_tabs": len(data.get("edge_tabs",[])),
                    "explorer": len(data.get("explorer",[])),
                    "id":cnt
                })
        except Exception as e:
            logger.error(f"Error reading session file {session_file}: {e}")
    
    return sessions

def delete_session(task_name):
    """Delete a saved session."""
    session_file = get_session_file(task_name)
    if not session_file.exists():
        return False, f"No saved session found for task: {task_name}"
    
    try:
        session_file.unlink()
        return True, f"Session deleted for task: {task_name}"
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return False, f"Failed to delete session: {e}"

def get_session_summary(task_name):
    """Get a summary of a saved session."""
    session_data = load_session(task_name)
    if not session_data:
        return None
    
    return {
        "task": task_name,
        "timestamp": session_data.get("timestamp"),
        "applications": [{
            "name": app.get("name"),
            "title": app.get("title")
        } for app in session_data.get("applications", [])],
        "chrome_tabs": [{
            "title": tab.get("title"),
            "url": tab.get("url")
        } for tab in session_data.get("chrome_tabs", [])],
        "brave_tabs": [{
            "title": tab.get("title"),
            "url": tab.get("url")
        } for tab in session_data.get("brave_tabs", [])],
        "edge_tabs": [{
            "title": tab.get("title"),
            "url": tab.get("url")
        } for tab in session_data.get("edge_tabs", [])],
        "explorer": [{
            "title": tab.get("title"),
            "path": tab.get("path")
        } for tab in session_data.get("explorer", [])]
    }