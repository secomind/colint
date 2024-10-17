from pathlib import Path

from ..params.black_params import BlackParams
from .format_commented_lines import format_commented_lines
from .format_docstring import format_script_docstrings


def docformat(path: Path | str, params: BlackParams):
    """Formats docstring and commented lines of a file.

    **Experimental** Reads and rewrites the input file so that docstrings and commented
    lines follow the google docstring guide lines.

    Args:
        path (Path | str): The path to the file that you wish to reformat.
        params (BlackParams): Parameters for configuring the formatter.
    """
    path = Path(path)
    format_commented_lines(path, params.line_length)
    format_script_docstrings(path, params.line_length)
