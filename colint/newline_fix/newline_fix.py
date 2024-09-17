from pathlib import Path

from ..utils.os_utils import get_valid_files
from ..utils.text_formatting_utils import TextModifiers, format_text


def __format_text(fname: str | Path, only_check: bool) -> str:
    formatted_fname = format_text(str(Path(fname).resolve()), TextModifiers.BOLD)
    if only_check:
        return f"{formatted_fname}: No newline at the end of file!"
    else:
        return f"{formatted_fname}: Added newline at the end of file."


def newline_fix(path: str, only_check: bool = False):
    files = get_valid_files(path)
    modified = False
    for fname in files:
        with Path(fname).open("rb+") as f:
            f.seek(-1, 2)
            last_byte = f.read(1)

            newline_missing = last_byte != b"\n"

            modified |= newline_missing

            if newline_missing:
                print(__format_text(fname, only_check))
            if newline_missing and not only_check:
                f.write(b"\n")
    return modified
