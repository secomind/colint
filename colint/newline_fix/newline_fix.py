import re
from pathlib import Path

from ..utils.os_utils import get_valid_files
from ..utils.text_styling_utils import TextModifiers, style_text


def __is_binary_file(fname: str | Path) -> bool:
    """Determine if a file is binary.

    This function checks if a given file is binary by reading the first
    1024 bytes and evaluating the presence of non-text characters.

    Args:
        fname (str | Path): The path to the file to be checked.

    Returns:
        bool: True if the file is binary, False if it is likely a text file.
    """
    if not Path(fname).is_file():
        return False
    textchars = (
        bytearray([7, 8, 9, 10, 12, 13, 27])
        + bytearray(range(0x20, 0x7F))
        + bytearray(range(0x80, 0x100))
    )
    with Path(fname).open("rb") as f:
        res = f.read(1024).translate(None, textchars)
    return bool(res)


def __ends_with_non_whitespace_newline(s: str) -> bool:
    """Check if a string ends with a newline preceded by a non-whitespace character.

    Args:
        s (str): The string to be checked.

    Returns:
        bool: True if the string ends with a non-whitespace character followed by a
            newline, False otherwise.
    """
    pattern = r"\S\n$"
    return re.search(pattern, s) is not None


def __style_text(fname: str | Path, only_check: bool) -> str:
    styled_fname = style_text(str(Path(fname).resolve()), TextModifiers.BOLD)
    if only_check:
        return f"{styled_fname}: No newline at the end of file!"
    else:
        return f"{styled_fname}: Added newline at the end of file."


def newline_fix(path: str, only_check: bool = False):
    """Ensure that all files in the specified path have a single newline at the end.

    This function iterates over all the valid files in the given directory and
    checks if they end with (only) a newline character. If a file does not end
    with a single newline, or it has trailing whitespaces it will print the
    issue. If `only_check` is False, it will also fix the file.

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
        if fname.endswith(".ipynb"):
            continue
        if __is_binary_file(fname):
            continue

        bad_eof = False

        with Path(fname).open("r+") as f:
            text = f.read()
            if len(text) == 0:
                continue
            if not __ends_with_non_whitespace_newline(text):
                bad_eof = True
            modified |= bad_eof

            if bad_eof:
                print(__style_text(fname, only_check))
        if bad_eof and not only_check:
            with Path(fname).open("w+") as f:
                f.write(f"{text.rstrip()}\n")
    return modified
