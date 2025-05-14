# import win32gui
# import subprocess
# import time
# from datetime import datetime
# import threading
# import requests
# import os

# LOG_FILE = "session_logs.txt"
# DEBUGGING_PORT = 9222

# def launch_browser_with_debugging():
#     # Try Brave first
#     brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
#     chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
#     launch_command = None

#     if os.path.exists(brave_path):
#         launch_command = f'"{brave_path}" --remote-debugging-port={DEBUGGING_PORT} --user-data-dir="C:/fleck_brave_profile"'
#     elif os.path.exists(chrome_path):
#         launch_command = f'"{chrome_path}" --remote-debugging-port={DEBUGGING_PORT} --user-data-dir="C:/fleck_chrome_profile"'
#     else:
#         print("❌ Neither Brave nor Chrome found.")
#         return

#     subprocess.Popen(launch_command, shell=True)
#     print("🌐 Browser launched with remote debugging enabled.")

# def get_active_window_title():
#     window = win32gui.GetForegroundWindow()
#     return win32gui.GetWindowText(window)

# def get_browser_tabs():
#     try:
#         response = requests.get(f"http://localhost:{DEBUGGING_PORT}/json")
#         tabs = response.json()
#         active_tabs = [tab['title'] for tab in tabs if tab['type'] == 'page']
#         return active_tabs
#     except Exception:
#         return []

# def start_session_tracking(log_file=LOG_FILE, interval=10):
#     launch_browser_with_debugging()  # Launch browser if needed

#     def tracker():
#         with open(log_file, 'a', encoding='utf-8') as f:
#             while True:
#                 try:
#                     win_title = get_active_window_title()
#                     browser_tabs = get_browser_tabs()
#                     active_tab = browser_tabs[0] if browser_tabs else "No active browser tab"

#                     f.write(f"{datetime.now()} | Window: {win_title} | Tab: {active_tab}\n")
#                     f.flush()
#                 except Exception as e:
#                     f.write(f"{datetime.now()} | ERROR: {str(e)}\n")
#                 time.sleep(interval)

#     tracking_thread = threading.Thread(target=tracker, daemon=True)
#     tracking_thread.start()
#     return tracking_thread







import win32gui
import time
from datetime import datetime
import threading
import requests
import os
import json
from pathlib import Path
from appdirs import user_data_dir

DEBUGGING_PORT = 9222
APP_NAME = "FleckCLI"
DATA_DIR = Path(user_data_dir(APP_NAME)+"/Data")
SESSIONS_DIR = DATA_DIR / "sessions"
LOGS_DIR = DATA_DIR / "logs"

def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

def get_browser_tabs():
    try:
        response = requests.get(f"http://localhost:{DEBUGGING_PORT}/json")
        tabs = response.json()
        return [tab['url'] for tab in tabs if tab['type'] == 'page']
    except:
        return []

def start_session_tracking(workspace_name, interval=10):
    log_file = f"{LOGS_DIR}/{workspace_name}_session_log.txt"
    state_file = f"{LOGS_DIR}/{workspace_name}_state.json"
    print(log_file)
    def tracker():
        while True:
            win_title = get_active_window_title()
            browser_tabs = get_browser_tabs()
            state = {
                'timestamp': datetime.now().isoformat(),
                'active_window': win_title,
                'browser_tabs': browser_tabs
            }
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(state) + '\n')
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f)
            time.sleep(interval)

    tracking_thread = threading.Thread(target=tracker, daemon=True)
    tracking_thread.start()
    return tracking_thread







# import win32gui
# import win32process
# import psutil
# import time
# from datetime import datetime
# import threading
# import requests
# import os
# import json

# DEBUGGING_PORT = 9222

# def get_active_window_title_and_app():
#     hwnd = win32gui.GetForegroundWindow()
#     pid = win32process.GetWindowThreadProcessId(hwnd)[1]
#     try:
#         process = psutil.Process(pid)
#         exe_path = process.exe()
#         title = win32gui.GetWindowText(hwnd)
#         return title, exe_path
#     except (psutil.NoSuchProcess, psutil.AccessDenied):
#         return None, None

# def get_browser_tabs():
#     try:
#         response = requests.get(f"http://localhost:{DEBUGGING_PORT}/json")
#         tabs = response.json()
#         return [tab['url'] for tab in tabs if tab['type'] == 'page']
#     except:
#         return []

# def get_foreground_apps():
#     app_paths = set()
#     for proc in psutil.process_iter(['exe', 'username']):
#         try:
#             if proc.info['exe'] and proc.info['username']:  # filters out system/background
#                 app_paths.add(proc.info['exe'])
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     return list(app_paths)

# def start_session_tracking(workspace_base_path, interval=10):
#     log_file = f"{workspace_base_path}_session_log.txt"
#     state_file = f"{workspace_base_path}_state.json"

#     def tracker():
#         while True:
#             win_title, exe_path = get_active_window_title_and_app()
#             browser_tabs = get_browser_tabs()
#             running_apps = get_foreground_apps()

#             state = {
#                 'timestamp': datetime.now().isoformat(),
#                 'active_window': win_title,
#                 'active_app_path': exe_path,
#                 'browser_tabs': browser_tabs,
#                 'running_apps': running_apps
#             }

#             with open(log_file, 'a', encoding='utf-8') as f:
#                 f.write(json.dumps(state) + '\n')
#             with open(state_file, 'w', encoding='utf-8') as f:
#                 json.dump(state, f, indent=2)

#             time.sleep(interval)

#     tracking_thread = threading.Thread(target=tracker, daemon=True)
#     tracking_thread.start()
#     return tracking_thread
