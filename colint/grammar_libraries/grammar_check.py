import tempfile
from pathlib import Path

from flake8.api import legacy as flake8

from ..params.flake8_params import Flake8Params
from ..utils.jupyter_utils import JupyterNotebokParser
from ..utils.os_utils import get_valid_files
from .flake8error import Flake8Error
from .get_custom_style_guide import get_custom_style_guide


def __report_to_errors(report: list[tuple], replace_fname: str | None = None) -> list[Flake8Error]:
    """
    Convert a flake8 report to a list of Flake8Error objects.

    Args:
        report (list[tuple]): A list of tuples representing flake8 errors; returned by flake8.
        replace_fname (str | None, optional): Filename to replace the original in the errors. Defaults to None.

    Returns:
        list[Flake8Error]: A list of Flake8Error objects.
    """
    all_errors = []
    for fname, errors, _ in report:
        fname_to_use = replace_fname if replace_fname else fname
        all_errors += [Flake8Error(fname_to_use, err) for err in errors]
    return all_errors


def __find_min_index(nums, target):
    """
    Find the minimum index in a list where the running sum of elements is greater than or equal to the target.

    Args:
        nums (list[int]): A list of integers.
        target (int): The target sum.

    Returns:
        int: The index where the running sum first exceeds or meets the target, or -1 if not found.
    """
    running_sum = 0
    for index, num in enumerate(nums):
        running_sum += num
        if running_sum >= target:
            return index
    return -1


def __report_from_string(style_guide: flake8.StyleGuide, text: str) -> list[Flake8Error]:
    """
    Generate a flake8 report from a string of code.

    Args:
        style_guide (StyleGuide): The flake8 (legacy) style guide object.
        text (str): The code to be checked.

    Returns:
        list[Flake8Error]: A list of Flake8Error objects.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(text.encode())
        temp_file_path = temp_file.name
    _ = style_guide.input_file(temp_file_path)
    results = style_guide._application.file_checker_manager.results.copy()
    Path(temp_file_path).unlink(missing_ok=True)
    return __report_to_errors(results)


def __code_check_jupyter_notebook(style_guide: flake8.StyleGuide, fname: Path | str) -> list[Flake8Error]:
    """
    Check a Jupyter notebook for flake8 errors.

    Args:
        style_guide (StyleGuide): The flake8 (legacy) style guide object.
        fname (Path | str): The path to the Jupyter notebook file.

    Returns:
        list[Flake8Error]: A list of Flake8Error objects.
    """
    nb = JupyterNotebokParser(fname)
    all_cells = [cell for cell in nb.code_cells(exclude_empty=True)]
    cells_size = [cell.size for cell in all_cells]
    text = "\n".join(cell.text for cell in all_cells)
    errors = __report_from_string(style_guide, text)

    for err in errors:
        err.filename = str(fname)
        cell_idx = __find_min_index(cells_size, err.line_number) + 1
        if cell_idx <= 0:
            continue
        err.cell_number = cell_idx
        err.line_number -= sum(cells_size[: cell_idx - 1])
    return errors


def code_check(path: str, params: Flake8Params) -> bool:
    """
    Check code files (Python scripts and Jupyter notebooks) for flake8 errors.

    Args:
        path (str): The path to the directory or file to be checked.
        params (Flake8Params): The flake8 parameters for the style guide.

    Returns:
        bool: True if there are any flake8 errors that are not ignored, False otherwise.
    """
    files = get_valid_files(path)

    python_scripts = [fname for fname in files if fname.endswith(".py")]
    jupyter_notebooks = [fname for fname in files if fname.endswith(".ipynb")]

    style_guide = get_custom_style_guide(params)

    _ = style_guide.check_files(python_scripts)
    report_python_scripts = style_guide._application.file_checker_manager.results.copy()
    errors = __report_to_errors(report_python_scripts)
    for nb_file in jupyter_notebooks:
        errors += __code_check_jupyter_notebook(style_guide, nb_file)

    errors = [
        error
        for error in errors
        if not error.should_be_ignored(ignore=params.extend_ignore, per_file_ignores=params.per_file_ignores)
    ]

    for err in errors:
        print(err.to_str())

    return len(errors) > 0
