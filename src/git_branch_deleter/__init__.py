import shutil
import subprocess
import sys
from pathlib import Path

import questionary


IGNORE_BRANCHES = {"main", "master", "develop"}

def get_branches() -> list[str]:
    """Return the list of local branch names."""
    try:
        out = subprocess.check_output(
            ["git", "branch", "--format", "%(refname:short)"], text=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running git: " + str(e), file=sys.stderr)
        sys.exit(1)
    return [b.strip() for b in out.splitlines() if b.strip()]


def delete_branches(branches: list[str], force: bool = False) -> bool:
    """Delete *branches* using git.

    Returns True if git exits 0, False otherwise.
    """
    flag = "-D" if force else "-d"
    cmd = ["git", "branch", flag, *branches]
    return subprocess.call(cmd) == 0


def ensure_git_repo() -> None:
    if not (Path.cwd() / ".git").exists():
        print("Not inside a Git repository. Aborting.", file=sys.stderr)
        sys.exit(1)


def run() -> None:
    if shutil.which("git") is None:
        print("git command not found in PATH.", file=sys.stderr)
        sys.exit(1)

    ensure_git_repo()

    branches = list(set(get_branches()) - IGNORE_BRANCHES)
    if not branches:
        print("No local branches found.")
        return

    selection = questionary.checkbox(
        "Select branches to delete (space to toggle, enter to confirm):",
        choices=branches,
        validate=lambda x: bool(x) or "Select at least one branch.",
    ).ask()

    if not selection:
        print("No branches selected. Aborted.")
        return

    force = questionary.confirm("Use force delete (-D)?", default=False).ask()

    summary = ", ".join(selection)
    if not questionary.confirm(
        f"Delete {len(selection)} branch(es): {summary}?", default=False
    ).ask():
        print("Aborted by user.")
        return

    print(f"Deleting branches: {summary}")
    if delete_branches(selection, force):
        print("Deletion complete.")
    else:
        print("git exited with errors. Some branches may remain.")


def main():
    try:
        run()
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
