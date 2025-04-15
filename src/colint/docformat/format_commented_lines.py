import ast
from pathlib import Path

from .format_text import format_text_with_prefix


def __find_commented_lines(script: str) -> set[int]:
    """Return the set of line numbers that are fully commented in the provided script.

    Args:
        script (str): The Python script as a single string.

    Returns:
        set[int]: A set of line numbers (0-indexed) that are fully commented.
    """
    tree = ast.parse(script)
    code_lines = {node.lineno for node in ast.walk(tree) if hasattr(node, "lineno")}
    return {
        idx
        for idx, line in enumerate(script.splitlines())
        if idx + 1 not in code_lines and line.lstrip().startswith("#")
    }


def __format_commented_line(line: str, line_length: int) -> str:
    """Format a commented line .

    Args:
        line (str): The original commented line to be formatted.
        line_length (int): The desired maximum line length for formatting.

    Returns:
        str: The reformatted commented line.
    """
    if not line.lstrip().startswith("#"):
        return line
    whitespaces = line.split("#")[0]
    length_whitespaces = whitespaces.count("\t") * 4 + whitespaces.count(" ")
    indent_level = length_whitespaces // 4
    line_content = line.split("#")[1].strip()
    formatted_lines = format_text_with_prefix(
        text=line_content,
        prefix=" " * indent_level * 4 + "# ",
        line_length=line_length,
    )
    return "\n".join(formatted_lines)


def get_formatted_commented_lines_script(script: str, line_length: int) -> str:
    """Format all fully commented lines in a Python script.

    Args:
        script (str): The Python script file to be processed.
        line_length (int): The maximum length for each line after formatting.

    Returns:
        str: The reformatted script.
    """
    commented_lines_idx = __find_commented_lines(script)
    new_lines = []
    for idx, line in enumerate(script.splitlines()):
        if idx in commented_lines_idx:
            new_lines.append(__format_commented_line(line, line_length))
        else:
            new_lines.append(line)
    new_script = "\n".join(new_lines)
    while new_script[-1] == "\n" and len(new_script) > 0:
        new_script = new_script[:-1]
    new_script += "\n"
    return new_script


def format_commented_lines(
    script_path: Path,
    line_length: int,
):
    """Format all fully commented lines in a Python script file at the given path.

    Args:
        script_path (Path): The path to the Python script file to be processed.
        line_length (int): The maximum length for each line after formatting.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    if not script_path.is_file():
        abs_path = str(script_path.absolute())
        raise FileNotFoundError(f"File {abs_path} not found.")
    with script_path.open("r") as f:
        script = f.read()
    new_script = get_formatted_commented_lines_script(script, line_length)
    with script_path.open("w+") as f:
        f.write(new_script)
