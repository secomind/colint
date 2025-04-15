from pathlib import Path

from ..utils.jupyter_utils import JupyterNotebokParser
from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text


def __style_text(fname: str | Path, only_check: bool) -> str:
    """Styles the file name for display.

    Args:
        fname (str | Path): The name or path of the file.
        only_check (bool): If True, returns a message indicating the file
            hasn't been cleared of outputs. Otherwise, indicates the file
            has been cleared.

    Returns:
        str: A styled string indicating the status of the file's outputs.
    """
    styled_fname = style_text(str(Path(fname).resolve()), TextModifiers.BOLD)

    if only_check:
        return f"{styled_fname}: has not been cleared of its outputs."
    return f"{styled_fname}: has been cleared of its outputs."


def __clean_notebook(fname: str | Path, only_check: bool) -> bool:
    """Clean outputs from a Jupyter notebook or check if it has outputs.

    Args:
        fname (str | Path): The name or path of the Jupyter notebook file.
        only_check (bool): If True, only checks for outputs without clearing them.
            If False, clears the outputs.

    Returns:
        bool: True if the notebook had outputs that were checked or cleared,
            False otherwise.
    """
    nb = JupyterNotebokParser(fname)
    modifications = False
    for cell in nb.code_cells():
        if not cell.has_output(picky=True):
            continue
        modifications = True
        if not only_check:
            cell.clear_output(reset_execution_count=True)
    if not only_check:
        nb.save(fname)
    return modifications


def jupyter_clean(path: str, only_check: bool) -> bool:
    """Clean outputs from all Jupyter notebooks in a directory or check outputs.

    Args:
        path (str): The directory path to search for Jupyter notebooks.
        only_check (bool): If True, only checks for outputs without clearing them.
            If False, clears the outputs.

    Returns:
        bool: True if any notebooks had outputs that were checked or cleared,
            False otherwise.
    """
    files = get_valid_files(path)
    notebooks = [fname for fname in files if fname.endswith(".ipynb")]
    modified = False
    for fname_nb in notebooks:
        nb_modified = __clean_notebook(fname_nb, only_check)
        if nb_modified:
            modified = True
            print(__style_text(fname_nb, only_check))
    return modified
