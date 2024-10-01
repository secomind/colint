import io
from pathlib import Path

import isort

from ..params.isort_params import IsortParams
from ..utils.jupyter_utils import JupyterNotebokParser
from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text

FILE_SORTED_MESSAGE = "! File has been sorted: "
FILE_NOT_SORTED_MESSAGE = "! File has not been sorted: "


def __style_message(f: Path, only_check: bool) -> str:
    styled_fname = style_text(str(f.resolve()), TextModifiers.BOLD)
    if only_check:
        return style_text(FILE_NOT_SORTED_MESSAGE, TextModifiers.ERROR) + styled_fname
    return FILE_SORTED_MESSAGE + styled_fname


def __isort_text(text: str, params: IsortParams) -> tuple[str, bool]:
    """Sort import statements in a given text using isort.

    Args:
        text (str): The input text containing import statements.
        params (IsortParams): The isort parameters to apply for import-sorting.

    Returns:
        tuple[str, bool]: A tuple containing the import-sorted text and a boolean indicating if changes were made.
    """
    # Create byte streams for input and output
    input_byte_stream = io.BytesIO(text.encode("utf-8"))
    input_text_stream = io.TextIOWrapper(input_byte_stream, encoding="utf-8")
    output_byte_stream = io.BytesIO()
    output_text_stream = io.TextIOWrapper(output_byte_stream, encoding="utf-8")

    has_been_sorted = isort.stream(
        input_text_stream, output_text_stream, profile=params.profile
    )

    # Retrieve the sorted text from the output stream
    output_text_stream.seek(0)
    return output_text_stream.read(), has_been_sorted


def __isort_jupyter_notebook(fname: str, only_check: bool, params: IsortParams) -> bool:
    """Sort import statements in a Jupyter notebook file.

    Args:
        fname (str): The filename of the Jupyter notebook.
        only_check (bool): Flag to indicate if only a check should be performed.
        params (IsortParams): The isort parameters to apply for sorting.

    Returns:
        bool: Boolean indicating if any imports have been sorted.
    """
    file_has_been_linted = False

    # Open and read the notebook as a JSON file
    nb = JupyterNotebokParser(fname)

    for cell in nb.code_cells(exclude_empty=True):
        output_text, has_been_linted = __isort_text(cell.text, params)
        file_has_been_linted = file_has_been_linted or has_been_linted

        if only_check:
            continue

        if has_been_linted:
            cell.text = output_text

    if not only_check:
        nb.save(fname)

    return file_has_been_linted


def sort_imports(path: str, only_check: bool, params: IsortParams) -> bool:
    """Sort import statements in all Python and Jupyter notebook files in the given path.

    Args:
        path (str): The directory path to search for files.
        only_check (bool): Flag to indicate if only a check should be performed.
        params (IsortParams): The isort parameters to apply for sorting.

    Returns:
        bool: Boolean indicating if any imports have been sorted in any file.
    """
    files = get_valid_files(path)

    some_file_has_been_sorted = False

    # Filter out Python and Jupyter notebook files
    script_files = [Path(f) for f in files if f.endswith(".py") and Path(f).is_file()]
    notebook_files = [
        Path(f) for f in files if f.endswith(".ipynb") and Path(f).is_file()
    ]

    # Process Python files
    for f in script_files:
        if only_check:
            file_not_linted = not isort.check_file(
                f,
                profile=params.profile,
                format_error="\033[F",
                format_success="\033[F",
            )
        else:
            file_not_linted = isort.file(
                f,
                profile=params.profile,
                format_error="\033[F",
                format_success="\033[F",
            )
        some_file_has_been_sorted = some_file_has_been_sorted or file_not_linted
        if file_not_linted:
            print(__style_message(f, only_check))

    # Process Jupyter notebook files
    for f in notebook_files:
        file_not_linted = __isort_jupyter_notebook(str(f), only_check, params)
        some_file_has_been_sorted = some_file_has_been_sorted or file_not_linted
        if file_not_linted:
            print(__style_message(f, only_check))

    return some_file_has_been_sorted
