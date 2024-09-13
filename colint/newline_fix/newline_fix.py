from pathlib import Path

from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text


def __style_text(fname: str | Path, only_check: bool) -> str:
    """
    Styles the filename by applying bold text styling and appends a
    message based on the file check status.

    Args:
        fname (str | Path): The filename to style.
        only_check (bool): A flag indicating if only a check is performed.

    Returns:
        str: The formatted string with the appropriate message.
    """
    styled_fname = style_text(str(Path(fname).resolve()), TextModifiers.BOLD)
    if only_check:
        return f"{styled_fname}: No newline at the end of file!"
    else:
        return f"{styled_fname}: Added newline at the end of file."


def newline_fix(path: str, only_check: bool = False):
    """
    Checks for missing newline characters at the end of files in the given
    directory path and adds a newline if missing.

    Args:
        path (str): The directory path to check for files.
        only_check (bool, optional): If True, only checks for newline without
                                     adding. Defaults to False.

    Returns:
        bool: True if any file was modified, False otherwise.
    """
    files = get_valid_files(path)
    modified = False
    for fname in files:
        with Path(fname).open("rb+") as f:
            f.seek(-1, 2)
            last_byte = f.read(1)

            newline_missing = last_byte != b"\n"

            modified |= newline_missing

            if newline_missing:
                print(__style_text(fname, only_check))
            if newline_missing and not only_check:
                f.write(b"\n")
    return modified
