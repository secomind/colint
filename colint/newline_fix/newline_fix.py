from pathlib import Path

from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text


def __style_text(fname: str | Path, only_check: bool) -> str:
    styled_fname = style_text(str(Path(fname).resolve()), TextModifiers.BOLD)
    if only_check:
        return f"{styled_fname}: No newline at the end of file!"
    else:
        return f"{styled_fname}: Added newline at the end of file."


def newline_fix(path: str, only_check: bool = False):
    """Ensure that all files in the specified directory have a newline at the end.

    This function iterates over all the valid files in the given directory and
    checks if they end with a newline character. If a file does not end with a
    newline, it prints the filename. If `only_check` is False, it also appends
    a newline to the end of the file.

    Args:
        path (str): The directory path containing files to check and/or fix.
        only_check (bool): If True, only checks for missing newlines without
            modifying files. Defaults to False.

    Returns:
        bool: True if any file was found without a newline at the end, False otherwise.
    """
    files = get_valid_files(path)
    modified = False
    for fname in files:
        with Path(fname).open("rb+") as f:
            try:
                f.seek(-1, 2)
                last_byte = f.read(1)
            except OSError:  # OSError is raised if file is empty
                continue  # if file is empty, ignore file.
            newline_missing = last_byte != b"\n"

            modified |= newline_missing

            if newline_missing:
                print(__style_text(fname, only_check))
            if newline_missing and not only_check:
                f.write(b"\n")
    return modified
