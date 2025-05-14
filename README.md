# FleckCLI 🧠📈

**FleckCLI** is a productivity-focused command-line tool that helps you manage tasks, track active sessions, monitor app and browser usage, and integrate Git seamlessly — all from your terminal. It's ideal for developers, students, or remote workers aiming to stay focused and organized.

---

## 📦 Installation

Install from PyPI (after publishing):

```bash
pip install fleckcli
```

Or install it locally from the repo

```bash
git clone https://github.com/your-username/fleckcli.git
cd fleckcli
pip install .
```

## 🧾 FleckCLI Command Reference

| Command            | Description                                         | Example Usage                              |
| ------------------ | --------------------------------------------------- | ------------------------------------------ |
| `add`              | Add a new todo to the current task                  | `fleck add "Write report" --priority high` |
| `create`           | Create a new workspace                              | `fleck create projectX`                    |
| `current`          | Show the currently active workspace                 | `fleck current`                            |
| `delete`           | Delete a todo from the current task                 | `fleck delete 3`                           |
| `delete-workspace` | Delete a saved workspace                            | `fleck delete-workspace`                   |
| `done`             | Mark a todo as done                                 | `fleck done 2`                             |
| `flag`             | Set priority for a todo                             | `fleck flag 2 high`                        |
| `focus`            | Enter Focus Mode and restore workspace              | `fleck focus projectX`                     |
| `gui`              | Open the workspace in the GUI viewer                | `fleck gui`                                |
| `gui-timer`        | Launch a GUI timer window for a todo                | `fleck gui-timer 4`                        |
| `list`             | List all todos for the current task with TUI        | `fleck list`                               |
| `pause`            | Pause a todo that's in progress                     | `fleck pause 2`                            |
| `progress`         | Mark a todo as in progress and start timer          | `fleck progress 1`                         |
| `restore`          | Restore a saved workspace for a specific task       | `fleck restore projectX`                   |
| `resume`           | Resume a paused todo                                | `fleck resume 3`                           |
| `save`             | Save the current workspace                          | `fleck save`                               |
| `show`             | Show details of current workspace                   | `fleck show`                               |
| `switch`           | Switch to another workspace and restore its session | `fleck switch projectY`                    |
| `tasks`            | List all available tasks                            | `fleck tasks`                              |
| `timer`            | Show a live timer for a todo in progress            | `fleck timer 5`                            |
| `track-session`    | Start session tracking (app + browser tab)          | `fleck track-session`                      |

## ✨ Features

### 🔄 Workspace Management (Multi-context Productivity)

- **Create, switch, save, and restore workspaces** — seamlessly transition between projects while preserving the session state.
- Workspaces store open applications, file explorers, and browser tabs (Chrome, Brave, Edge), enabling full context switching.

### 📋 Smart Task & Todo System

- Add tasks with **priority tagging** (`high`, `medium`, `low`, `none`).
- Mark tasks as **in progress**, **done**, or **paused**, with a **live timer** to track effort.
- Todos are **workspace-bound**, giving context-aware productivity.

### 📈 Session Tracking & Log Management

- Automatically tracks:
  - Active **applications**
  - **Browser tabs** (Chrome, Brave, Edge)
  - File explorers
- Logs are saved in structured `.txt` files per session for review or future reference.

### 🧠 Focus Mode (Deep Work Support)

- Closes non-essential apps and restores only those relevant to your task.
- Designed to support distraction-free, flow-state work sessions.

### 🖥️ GUI & TUI Interfaces

- Rich **terminal UI (TUI)** for managing and viewing todos.
- Interactive **GUI timer** for visual task tracking.
- GUI-based **workspace viewer** to browse the session context.

### 📊 Progress Visualization

- Real-time live timers for in-progress tasks.
- Session and timer data stored for historical tracking and personal analytics.

### 🔐 Git-Integrated Context (Optional)

- Optional integration with `GitPython` to fetch Git repo context for project-specific productivity.

### 📦 Lightweight & Portable

- Fully CLI-based — no bloat.
- Cross-platform directory handling using `appdirs` ensures safe and consistent data storage.

---

## 🧑‍💻 Use Cases

| Role            | How FleckCLI Helps                                                                 |
| --------------- | ---------------------------------------------------------------------------------- |
| **Developers**  | Save and restore coding sessions with editors, terminals, and browser tabs intact. |
| **Writers**     | Focus mode for deep writing sessions and context-based notes or research tabs.     |
| **Researchers** | Manage context-rich sessions including PDFs, notebooks, and datasets.              |
| **Students**    | Track study time, manage subject-based todos, and restore study environments.      |
| **Freelancers** | Switch between client projects without losing track of open resources.             |

---

## 👤 Author

**FleckCLI** is built and maintained by **Atharva Goliwar**.  
If you found this tool useful or want to contribute, feel free to fork, star 🌟, or raise an issue on the [GitHub repository](https://github.com/AtharvaGoliwar/FleckCLI).

---
