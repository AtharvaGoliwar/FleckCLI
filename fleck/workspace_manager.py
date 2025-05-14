import os
import json
import subprocess

DEBUGGING_PORT = 9222

def save_workspace_state(workspace_name):
    # This function is handled by the session tracker
    pass  # State is continuously saved by the tracker

def restore_workspace_state(workspace_name):
    state_file = f"{workspace_name}_state.json"
    if not os.path.exists(state_file):
        print(f"No saved state for workspace '{workspace_name}'.")
        return

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    # Restore browser tabs
    browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(browser_path):
        browser_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    if not os.path.exists(browser_path):
        print("Browser not found.")
        return

    for url in state.get('browser_tabs', []):
        subprocess.Popen([browser_path, url])










# workspace_manager.py
# import os
# import json
# import subprocess
# import psutil
# import time

# CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
# BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# def is_process_running(exe_path):
#     for proc in psutil.process_iter(['exe']):
#         try:
#             if proc.info['exe'] and os.path.normcase(proc.info['exe']) == os.path.normcase(exe_path):
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     return False

# def launch_chrome_debugging_if_needed():
#     chrome_path = CHROME_PATH if os.path.exists(CHROME_PATH) else BRAVE_PATH
#     if not os.path.exists(chrome_path):
#         print("Chrome/Brave not found.")
#         return None

#     if not is_process_running(chrome_path):
#         subprocess.Popen([
#             chrome_path,
#             "--remote-debugging-port=9222",
#             "--user-data-dir=%TEMP%\\remote-profile"
#         ])
#         time.sleep(2)  # Give it a moment to launch
#     return chrome_path

# def restore_workspace_state(workspace_base_path):
#     state_file = f"{workspace_base_path}_state.json"
#     if not os.path.exists(state_file):
#         print(f"No saved state for workspace at '{workspace_base_path}'.")
#         return

#     with open(state_file, 'r', encoding='utf-8') as f:
#         state = json.load(f)

#     # Restore Chrome/Brave
#     chrome_path = launch_chrome_debugging_if_needed()
#     if chrome_path:
#         for url in state.get('browser_tabs', []):
#             subprocess.Popen([chrome_path, url])

#     # Restore applications
#     restored = set()
#     for app_path in state.get('running_apps', []):
#         if os.path.exists(app_path) and app_path not in restored:
#             if not is_process_running(app_path):
#                 try:
#                     subprocess.Popen(app_path)
#                     restored.add(app_path)
#                 except Exception as e:
#                     print(f"Could not start {app_path}: {e}")

