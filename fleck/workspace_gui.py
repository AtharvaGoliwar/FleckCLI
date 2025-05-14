import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import session_manager
sys.path.append(str(Path(__file__).parent.parent))
from fleck.session_manager import load_session, restore_session

class WorkspaceViewer(tk.Tk):
    def __init__(self, task_name):
        super().__init__()
        
        self.task_name = task_name
        self.title(f"Workspace: {task_name}")
        self.geometry("800x600")
        
        # Load session data
        self.session_data = load_session(task_name)
        if not self.session_data:
            messagebox.showerror("Error", f"No session data found for task: {task_name}")
            self.destroy()
            return
        
        # Create tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add tabs
        self.create_apps_tab()
        self.create_chrome_tab()
        self.create_brave_tab()
        self.create_explorer_tab()
        self.create_edge_tab()
        self.create_summary_tab()
        
        # Create restore button
        restore_frame = ttk.Frame(self)
        restore_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(restore_frame, text="Restore This Workspace", 
                  command=self.restore_workspace).pack(side='right')
    
    def create_apps_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Applications")
        
        apps = self.session_data.get("applications", [])
        
        # Create treeview
        columns = ("name", "title", "path")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Define headings
        tree.heading("name", text="Application")
        tree.heading("title", text="Window Title")
        tree.heading("path", text="Path")
        
        # Define columns
        tree.column("name", width=150)
        tree.column("title", width=300)
        tree.column("path", width=300)
        
        # Add data
        for app in apps:
            tree.insert("", "end", values=(
                app.get("name", ""),
                app.get("title", ""),
                app.get("path", "")
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def create_chrome_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Chrome Tabs")
        
        tabs = self.session_data.get("chrome_tabs", [])
        
        # Create treeview
        columns = ("title", "url")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title", text="Tab Title")
        tree.heading("url", text="URL")
        
        # Define columns
        tree.column("title", width=300)
        tree.column("url", width=450)
        
        # Add data
        for tab_data in tabs:
            tree.insert("", "end", values=(
                tab_data.get("title", ""),
                tab_data.get("url", "")
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def create_brave_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Brave Tabs")
        
        tabs = self.session_data.get("brave_tabs", [])
        
        # Create treeview
        columns = ("title", "url")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title", text="Tab Title")
        tree.heading("url", text="URL")
        
        # Define columns
        tree.column("title", width=300)
        tree.column("url", width=450)
        
        # Add data
        for tab_data in tabs:
            tree.insert("", "end", values=(
                tab_data.get("title", ""),
                tab_data.get("url", "")
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def create_edge_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Edge Tabs")
        
        tabs = self.session_data.get("edge_tabs", [])
        
        # Create treeview
        columns = ("title", "url")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title", text="Tab Title")
        tree.heading("url", text="URL")
        
        # Define columns
        tree.column("title", width=300)
        tree.column("url", width=450)
        
        # Add data
        for tab_data in tabs:
            tree.insert("", "end", values=(
                tab_data.get("title", ""),
                tab_data.get("url", "")
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def create_explorer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="File Explorer Tabs")
        
        tabs = self.session_data.get("explorer", [])
        
        # Create treeview
        columns = ("title", "path")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title", text="Tab Title")
        tree.heading("path", text="Path")
        
        # Define columns
        tree.column("title", width=300)
        tree.column("path", width=450)
        
        # Add data
        for tab_data in tabs:
            tree.insert("", "end", values=(
                tab_data.get("title", ""),
                tab_data.get("url", "")
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def create_summary_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Summary")
        
        # Create summary frame
        summary_frame = ttk.LabelFrame(tab, text="Session Summary")
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get counts
        app_count = len(self.session_data.get("applications", []))
        chrome_count = len(self.session_data.get("chrome_tabs", []))
        brave_count = len(self.session_data.get("brave_tabs", []))
        exp_count = len(self.session_data.get("explorer",[]))
        edge_count = len(self.session_data.get("edge_tabs",[]))
        
        # Format timestamp
        timestamp = "Unknown"
        if self.session_data.get("timestamp"):
            try:
                dt = datetime.fromisoformat(self.session_data["timestamp"])
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        # Add labels
        ttk.Label(summary_frame, text=f"Task Name: {self.task_name}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=f"Last Saved: {timestamp}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=f"Applications: {app_count}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=f"Chrome Tabs: {chrome_count}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=f"Brave Tabs: {brave_count}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(summary_frame,text=f"Edge Tabs: {edge_count}").pack(anchor="w",padx=5,pady=2)
        ttk.Label(summary_frame, text=f"Explorer Paths: {exp_count}").pack(anchor="w", padx=5, pady=2)
    
    def restore_workspace(self):
        """Restore the workspace."""
        if messagebox.askyesno("Restore Workspace", 
                              f"Are you sure you want to restore the workspace for '{self.task_name}'?"):
            success, message = restore_session(self.task_name)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

def main():
    if len(sys.argv) != 2:
        print("Usage: python workspace_gui.py <task_name>")
        return
    
    task_name = sys.argv[1]
    app = WorkspaceViewer(task_name)
    app.mainloop()

if __name__ == "__main__":
    main()