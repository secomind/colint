import argparse
import sys
from pathlib import Path

from .clean_jupyter.clean_jupyter import jupyter_clean
from .code_format.code_format import format_code
from .grammar_libraries.grammar_check import code_check
from .newline_fix.newline_fix import newline_fix
from .params.params import Params
from .sort_libraries.sorter import sort_imports

config_file = Path(__file__).parent / "pyproject.toml"
params = Params.from_toml(config_file)

COMMANDS = [
    "clean-jupyter",
    "code-format",
    "grammar-check",
    "lint",
    "newline-fix",
    "sort-libraries",
]


def perform_operation(key: str, path: str, only_check: bool) -> bool:
    """Perform a specified operation on a given directory or file path.

    Args:
        key (str): The command specifying the operation to perform.
            Must be one of the following:
            [
                'sort-libraries',
                'code-format',
                'grammar-check',
                'newline-fix',
                'clean-jupyter',
            ].
        path (str): The path to the directory or file to perform the operation on.
        only_check (bool): If True, performs a check without modifying the files.

    Returns:
        bool: True if the operation is performed successfully, False otherwise.

    Raises:
        KeyError: If the provided key is not in COMMANDS or is 'lint'.
    """
    if key not in COMMANDS or key == "lint":
        raise KeyError(f'Cannot perform operation "{key}".')
    if key == "clean-jupyter":
        return jupyter_clean(path, only_check)
    if key == "code-format":
        return format_code(path, only_check, params.black)
    if key == "grammar-check":
        return code_check(path, params.flake8)
    if key == "newline-fix":
        return newline_fix(path, only_check)
    assert key == "sort-libraries"
    return sort_imports(path, only_check, params.isort)


def main():
    """Run the main entry point of the application.

    This function serves as the starting point for the script.
    It initializes the process and coordinates the overall workflow.

    Args:
        None

    Returns:
        None
    """
    arg_parser = argparse.ArgumentParser(
        description="Handles various commands related to directories and notebooks.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    arg_parser.add_argument(
        "command",
        choices=COMMANDS,
        help=(
            "Specify the command to execute. Options are:\n"
            "  - sort-libraries: Sorts and organizes the library imports.\n"
            "  - code-format: Formats the code according to defined style guides.\n"
            "  - grammar-check: Checks for and corrects grammatical/styling errors in code and docstrings.\n"
            "  - newline-fix: Fixes newline inconsistencies in the files.\n"
            "  - clean-jupyter: Cleans Jupyter notebook files by removing unnecessary metadata and outputs.\n"
            '  - lint: Performs all the operations above, but "clean-jupyter". To also use "clean-jupyter" use the --clean-notebooks flag.'
        ),
    )
    arg_parser.add_argument(
        "path_to_dir", help="Provide the path to the directory that needs linting."
    )

    arg_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Enable check mode.\n"
            "In this mode, linting will not modify files; it will only check for issues."
        ),
    )
    arg_parser.add_argument(
        "--clean-notebooks",
        action="store_true",
        help=(
            "Enable clean-notebooks mode.\n"
            'If "lint" command is selected, this adds a procedure to clean jupyter notebooks.\n'
            "If another command is used, it has no effect."
        ),
    )

    args = arg_parser.parse_args()

    command = args.command
    lint_dir = Path(args.path_to_dir)
    only_check = args.check
    clean_notebooks = args.clean_notebooks

    if not lint_dir.is_dir() and not lint_dir.is_file():
        print(f"Error: Path to directory '{lint_dir}' is not valid.")
        sys.exit(1)

    if command != "lint":
        res = perform_operation(command, str(lint_dir.resolve()), only_check)
        sys.exit(res)

    commands_to_perform = [
        c for c in COMMANDS if c != "lint" and (c != "clean-jupyter" or clean_notebooks)
    ]
    res = False
    for c in commands_to_perform:
        res |= perform_operation(c, lint_dir, only_check)
    sys.exit(res)


if __name__ == "__main__":
    main()
