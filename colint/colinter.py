import os
import subprocess
import sys

import toml

config = toml.load(os.path.dirname(__file__) + "/pyproject.toml")


def run_command(command):
    """Run a shell command."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        sys.exit(1)


def code_format(only_check: bool, args="."):
    """Run black code formatter."""
    line_length = config["tool"]["black"].get("line-length", 80)
    exclude = config["tool"]["black"].get("exclude", "")
    check_string = "--check" if only_check else ""
    run_command(f"python3 -m black --line-length {line_length} --exclude '{exclude}' {check_string} {args}")
    print(args)


def flake_lint(_, args="."):
    """Run flake8 linter."""
    exclude = ",".join(config["tool"]["flake8"].get("exclude", []))
    extend_ignore = ",".join(config["tool"]["flake8"].get("extend-ignore", []))
    per_file_ignores = config["tool"]["flake8"].get("per-file-ignores", "").replace("\n", "")
    run_command(
        f"python3 -m flake8 --exclude {exclude} --extend-ignore {extend_ignore} --per-file-ignores='{per_file_ignores}' {args} "
    )


def isort(only_check: bool, args="."):
    """Run isort for import sorting."""
    profile = config["tool"]["isort"].get("profile", "black")
    skip_glob = ",".join(config["tool"]["isort"].get("skip_glob", []))
    check_string = "--check-only" if only_check else ""
    run_command(f"python3 -m isort {args} --profile {profile} --skip-glob '{skip_glob}' {check_string}")


def vulture(_, args="."):
    """Run vulture."""
    exclude = ",".join(config["tool"]["vulture"].get("exclude", []))
    run_command(f"python3 -m vulture {args} --exclude '{exclude}'")


def type_check(_, args="."):
    """Run mypy for type checking."""
    python_version = config["tool"]["mypy"].get("python_version", "3.8")
    overrides = " ".join(
        [f"--exclude '{mod}'" for override in config["tool"]["mypy"].get("overrides", []) for mod in override["module"]]
    )
    run_command(f"python3 -m mypy {args}/*.py --python-version {python_version} {overrides}")


def lint(only_check: bool, args="."):
    """Run all linting tools: isort, black, flake8."""
    isort(only_check, args)
    code_format(only_check, args)
    flake_lint(only_check, args)


def clean():
    """Clean up Python bytecode and cache files."""
    run_command('find . -type f -name "*.py[co]" -delete')
    run_command('find . -type d -name "__pycache__" -delete')


def main():
    tasks = {
        "code-format": code_format,
        "flake-lint": flake_lint,
        "isort": isort,
        "vulture": vulture,
        "type-check": type_check,
        "lint": lint,
        "clean": clean,
    }

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <task> [args]")
        sys.exit(1)

    task = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else ["."]

    only_check = "--check" in args
    if only_check:
        args.remove("--check")

    if task in tasks:
        tasks[task](only_check, *args)
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    print("Done!")
