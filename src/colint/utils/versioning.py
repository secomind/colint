import os
from importlib.metadata import PackageNotFoundError, version

from git import Repo


def _get_version_str() -> str:
    try:
        return version("colint")
    except PackageNotFoundError:
        return "(version info not found)"


def _get_last_commit_date():
    try:
        repo = Repo(
            os.path.dirname(os.path.abspath(__file__)), search_parent_directories=True
        )
        commit = next(repo.iter_commits("HEAD", max_count=1))
        return commit.committed_datetime.strftime("%Y-%m-%d")
    except Exception:
        return "unknown"


def get_versioning() -> str:
    """Get versioning string with the package version and last commit date.

    Returns:
        str: A string containing the package name, version, and the date of the
             last commit.
    """
    return f"colint {_get_version_str()} (last updated: {_get_last_commit_date()})"
