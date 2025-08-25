from pathlib import Path

import git

from .exceptions import NotValidPath


def get_git_repo(path: str) -> git.Repo | None:
    """Retrieve a Git repository object from the specified path.

    Args:
        path (str): The directory path to search for a Git repository.

    Returns:
        git.Repo: The Git repository object if found.
        None: If the path is not a valid Git repository.
    """
    try:
        # Try to return the git repository object,
        # searching in parent directories as well
        repo = git.Repo(path, search_parent_directories=True)
        return repo
    except git.exc.InvalidGitRepositoryError:
        # If not a valid git repository, return None
        return None


def get_valid_files(path: str | Path) -> list[str]:
    """Retrieve a list of valid file paths in the specified directory.

    It excludes files in the '.git' directory and ignored files according to Git.

    Args:
    path (str): The path to a directory or a file.

    Returns:
    list[str]: A sorted list of valid file paths.

    Raises:
    NotValidPath: If the provided path is not a valid directory or a valid file.
    """
    if Path(path).is_file():
        return [str(path)]

    if not Path(path).is_dir():
        raise NotValidPath(f"Path {path} is not a valid directory.")

    repo = get_git_repo(path)
    # Get all files in the directory recursively,
    # excluding any files in the '.git' directory
    all_files_path = set(
        f for f in Path(path).rglob("*") if f.is_file() and ".git" not in f.parts
    )

    parent_directories = list(set(str(f.parent) for f in all_files_path))
    if repo:
        ignored_directories = set(repo.ignored(parent_directories))
    else:
        ignored_directories = set()
    possible_files = [
        str(f) for f in all_files_path if str(f.parent) not in ignored_directories
    ]
    valid_files = set(possible_files)

    if repo:  # If a git repository exists, remove files in gitignore
        batch_size = 1_000
        for k in range(0, len(possible_files), batch_size):
            repo_ignore = set(repo.ignored(possible_files[k : k + batch_size]))
            valid_files.difference_update(repo_ignore)
    return sorted(list(valid_files))
