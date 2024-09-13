from pathlib import Path

from black import Mode, format_file_contents

from ..params.black_params import BlackParams
from ..utils.jupyter_utils import JupyterNotebokParser
from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text


def __get_black_mode(params: BlackParams) -> Mode:
    """
    Create a Black formatter Mode instance based on the provided parameters.

    Args:
        params (BlackParams): The parameters to customize the Black formatter mode.

    Returns:
        Mode: A Mode instance configured with the provided parameters.
    """
    return Mode(
        line_length=params.line_length,
        target_versions=set(params.target_version),
        preview=params.preview,
        unstable=params.unstable,
    )


def __style_black_message(fname: str | Path, only_check: bool) -> str:
    """
    Format a message indicating whether a file would have been or has been reformatted.

    Args:
        fname (str | Path): The file name.
        only_check (bool): Whether the formatter is running in "check only" mode.

    Returns:
        str: A formatted message string.
    """
    styled_fname = style_text(str(Path(fname).resolve()), TextModifiers.BOLD)

    if only_check:
        return f"{styled_fname}: would have been reformatted."
    else:
        return f"{styled_fname}: has been reformatted"


def format_notebook(nb_path: str | Path, only_check: bool, mode: Mode) -> bool:
    """
    Format the code in a Jupyter notebook using Black.

    Args:
        nb_path (str | Path): The path to the Jupyter notebook file.
        only_check (bool): Whether to only check for formatting changes or to apply them.
        mode (Mode): The Black formatter mode to use.

    Returns:
        bool: True if the notebook was modified, False otherwise.
    """
    nb = JupyterNotebokParser(nb_path)
    modified = False
    for cell in nb.code_cells():
        try:
            formatted_code = format_file_contents(cell.text, fast=True, mode=mode)
            modified |= formatted_code != cell.text
            cell.text = formatted_code
        except Exception as e:
            print(f"Error formatting cell: {e}")
    if modified and not only_check:
        nb.save(nb_path)
    return modified


def format_script(input_path: str | Path, only_check: bool, mode: Mode) -> bool:
    """
    Format the code in a Python script using Black.

    Args:
        input_path (str | Path): The path to the Python script file.
        only_check (bool): Whether to only check for formatting changes or to apply them.
        mode (Mode): The Black formatter mode to use.

    Returns:
        bool: True if the script was modified, False otherwise.
    """
    text = Path(input_path).read_text(encoding="utf8")
    formatted_code = format_file_contents(text, fast=True, mode=mode)
    modified = formatted_code != text
    if modified and not only_check:
        Path(input_path).write_text(formatted_code, encoding="utf8")
    return modified


def format_code(path: str, only_check: bool, params: BlackParams) -> bool:
    """
    Format the code in Python scripts and Jupyter notebooks within the given path using Black.

    Args:
        path (str): The root directory path to search for files.
        only_check (bool): Whether to only check for formatting changes or to apply them.
        params (BlackParams): Parameters for configuring the Black formatter.

    Returns:
        bool: True if any file was modified, False otherwise.
    """
    mode = __get_black_mode(params)
    files = get_valid_files(path)

    script_files = [Path(f) for f in files if f.endswith(".py") and Path(f).is_file()]
    notebook_files = [Path(f) for f in files if f.endswith(".ipynb") and Path(f).is_file()]

    any_file_not_linted = False

    for file in script_files:
        modified = format_script(file, only_check, mode)
        any_file_not_linted |= modified
        if modified:
            print(__style_black_message(file, only_check))

    for file in notebook_files:
        modified = format_notebook(file, only_check, mode)
        any_file_not_linted |= modified
        if modified:
            print(__style_black_message(file, only_check))

    return any_file_not_linted
