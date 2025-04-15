import argparse
import sys
from pathlib import Path

from .clean_jupyter.clean_jupyter import jupyter_clean
from .code_format.code_format import format_code
from .docformat.docformat import docformat
from .grammar_libraries.grammar_check import code_check
from .newline_fix.newline_fix import newline_fix
from .params.params import Params
from .sort_libraries.sorter import sort_imports

config_file = Path(__file__).parent / "config.toml"
params = Params.from_toml(config_file)

COMMANDS = {
    "clean-jupyter",
    "code-format",
    "grammar-check",
    "lint",
    "newline-fix",
    "sort-libraries",
    "docformat",
}


def get_operations():
    """Get mapping of operations to their implementation functions."""
    return {
        "clean-jupyter": lambda p, c: jupyter_clean(p, c),
        "code-format": lambda p, c: format_code(p, c, params.black),
        "grammar-check": lambda p, c: code_check(p, params.flake8),
        "newline-fix": lambda p, c: newline_fix(p, c),
        "sort-libraries": lambda p, c: sort_imports(p, c, params.isort),
    }


def perform_operation(key: str, path: Path, only_check: bool) -> bool:
    """Perform a specified operation on a given directory or file path.

    Args:
        key: The command specifying the operation to perform
        path: The path to the directory or file
        only_check: If True, performs a check without modifying files

    Returns:
        bool: True if any issues were found, False if clean

    Raises:
        KeyError: If the provided key is not a valid command
    """
    operations = get_operations()
    if key not in operations:
        raise KeyError(f'Invalid operation "{key}"')
    return operations[key](str(path.resolve()), only_check)


def validate_path(path: Path, command: str) -> None:
    """Validate the provided path based on command requirements."""
    if not path.exists():
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    if command == "docformat" and not path.is_file():
        print("Error: docformat only works on a single file.")
        sys.exit(1)


def get_lint_commands(clean_notebooks: bool):
    """Get the list of commands to run during lint operation."""
    commands = ["sort-libraries", "code-format", "grammar-check", "newline-fix"]
    if clean_notebooks:
        commands = ["clean-jupyter"] + commands
    return commands


def run_tool(args: argparse.Namespace) -> None:
    """Execute the linting tool with provided arguments."""
    path = Path(args.path_to_dir)
    validate_path(path, args.command)

    if args.command == "docformat":
        docformat(path, params.black)
        sys.exit(0)

    if args.command != "lint":
        result = perform_operation(args.command, path, args.check)
        sys.exit(1 if result else 0)

    has_issues = False
    for cmd in get_lint_commands(args.clean_notebooks):
        try:
            cmd_result = perform_operation(cmd, path, args.check)
            has_issues = has_issues or cmd_result
        except Exception as e:
            print(f"Error during {cmd}: {str(e)}")
            has_issues = True

    sys.exit(1 if has_issues else 0)


def main():
    """Main entry point for the linting tool."""
    parser = argparse.ArgumentParser(
        description="Code linting and formatting tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "command",
        choices=COMMANDS,
        help=(
            "Available commands:\n"
            "  - sort-libraries: Sort and organize imports\n"
            "  - code-format: Format code according to style guides\n"
            "  - grammar-check: Check code and docstring style\n"
            "  - newline-fix: Fix newline inconsistencies\n"
            "  - clean-jupyter: Clean Jupyter notebooks\n"
            "  - lint: Run all checks except clean-jupyter\n"
            "  - docformat: Experimental docstring formatting (single file only)"
        ),
    )

    parser.add_argument(
        "path_to_dir",
        help="Path to target directory or file",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without modifying files",
    )

    parser.add_argument(
        "--clean-notebooks",
        action="store_true",
        help="Include notebook cleaning in lint command",
    )

    args = parser.parse_args()
    run_tool(args)


if __name__ == "__main__":
    main()
