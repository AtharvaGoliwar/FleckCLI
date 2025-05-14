from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from rich.console import Console
from pathlib import Path

console = Console()

def get_repo():
    """Returns the Git repo object from the current working directory, if valid."""
    cwd = Path.cwd()
    try:
        repo = Repo(cwd, search_parent_directories=True)
        if not repo.remotes:
            console.print(f"[red]✗ No Git remote configured (like 'origin') in {repo.working_dir}[/red]")
            return None
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError):
        console.print(f"[red]✗ No Git repo found in or above {cwd}[/red]")
        return None

def git_push(commit_message="Update tasks"):
    repo = get_repo()
    if not repo:
        return

    try:
        repo.git.add(all=True)
        repo.index.commit(commit_message)

        if 'origin' not in repo.remotes:
            console.print("[red]✗ 'origin' remote not found. Cannot push.[/red]")
            return

        repo.remotes.origin.push()
        console.print("[green]✓ Changes committed and pushed to 'origin'.[/green]")

    except GitCommandError as e:
        console.print(f"[red]✗ Git push failed:[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗ Unexpected error during push:[/red] {e}")
