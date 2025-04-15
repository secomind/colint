import ast
import re
from pathlib import Path

from .apply_google_style import apply_google_style

__docstring_pattern = re.compile(r"(\"\"\".*?\"\"\"|'''.*?''')", re.DOTALL)


def __is_docstring(node: ast.AST) -> bool:
    """Check if the given AST node is a docstring node.

    Args:
        node (ast.AST): An Abstract Syntax Tree (AST) node.

    Returns:
        bool: True if the node is a docstring, False otherwise.
    """
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)


def __should_add_indent(node: ast.AST) -> bool:
    """Check if the given AST node should cause an increase in indentation level.

    Args:
        node (ast.AST): An AST node.

    Returns:
        bool: True if the node represents a control structure or block, False otherwise.
    """
    return isinstance(
        node,
        (
            ast.AsyncFor,
            ast.AsyncFunctionDef,
            ast.AsyncWith,
            ast.ClassDef,
            ast.For,
            ast.FunctionDef,
            ast.If,
            ast.Try,
            ast.While,
            ast.With,
        ),
    )


def __calculate_indentation_levels(script: str) -> dict[int, int]:
    """Calculate indentation levels for each line of the given Python script.

    Args:
        script (str): The Python script as a string.

    Returns:
        dict[int, int]: A   dictionary  mapping  line  numbers  to  their  corresponding
            indentation levels.
    """
    tree = ast.parse(script)
    indentation_levels = {}

    def walk(node, level):
        for child in ast.iter_child_nodes(node):
            should_add_indent = __should_add_indent(child)
            if hasattr(child, "lineno") and child.lineno not in indentation_levels:
                indentation_levels[child.lineno] = (level, should_add_indent)

            if should_add_indent:
                walk(child, level + 1)
            else:
                walk(child, level)

    walk(tree, 0)

    return indentation_levels


def __extract_docstrings(script: str) -> list[tuple[int, int]]:
    """Extract the positions of docstrings in the given Python script.

    Args:
        script (str): The Python script as a string.

    Returns:
        list[tuple[int, int]]: A  list of tuples representing the start and end lines of
            each docstring.
    """
    tree = ast.parse(script)

    docstring_lines = list()

    for node in ast.walk(tree):
        if __is_docstring(node):
            start_lineno = node.lineno
            end_lineno = node.end_lineno
            docstring_lines.append((start_lineno - 1, end_lineno - 1))
    return docstring_lines


def __split_into_paragraphs(text: str) -> list[str]:
    """Split a block of text into paragraphs based on empty lines.

    Args:
        text (str): A block of text.

    Returns:
        list[str]: A  list  of paragraphs (strings) where each paragraph is separated by
            empty lines.
    """
    lines = text.splitlines()

    paragraphs = []
    current_paragraph = []
    empty_line_count = 0

    for line in lines:
        if line.strip() == "":
            empty_line_count += 1
        else:
            empty_line_count = 0

        if empty_line_count >= 1:
            if current_paragraph:
                paragraphs.append("\n".join(current_paragraph))
                current_paragraph = []
            empty_line_count = 0
        else:
            if line.strip() != "":
                current_paragraph.append(line)
    if current_paragraph:
        paragraphs.append("\n".join(current_paragraph))

    return paragraphs


def __format_docstring(docstring: str) -> list[str]:
    """Format a docstring and organize its content.

    Remove the surrounding triple quotes and organize content into paragraphs.

    Args:
        docstring (str): The original docstring including triple quotes.

    Returns:
        list[str]: A list of formatted docstring lines.
    """
    docstring_content = docstring[3:-3].strip()
    if len(docstring_content) == 0:
        return ""
    new_docstring = '"' * 3 + docstring_content + "\n" + '"' * 3

    paragraphs = __split_into_paragraphs(new_docstring)
    result = []

    for k, p in enumerate(paragraphs):
        if k > 0:
            result.append("")
        result += p.splitlines()
    return result


def __format_complete_docstring(
    docstring_text: str,
    indent_node: tuple[int, bool],
) -> tuple[list[str], list[str], int]:
    """Format a complete docstring, get indentation and extract the docstring content.

    It  removes  empty docstrings, merge consecutive docstrings, and handle what happens
    if docstring starts on a non-empty line.

    Args:
        docstring_text (str): The docstring text to format.
        indent_node (tuple[int, bool]): A  tuple  containing  the  indentation level and
            whether to increase it.

    Returns:
        tuple[list[str], list[str], int]: A   tuple  containing  the  lines  before  the
            docstring, the formatted docstring, and the updated indentation level.
    """
    indent_level, indent_adder = indent_node

    docstring_matches = list(__docstring_pattern.finditer(docstring_text))
    if len(docstring_matches) == 0:
        return ([docstring_text], [], indent_level)
    idx = docstring_matches[0].start()
    str_start = docstring_text[:idx].strip()
    if len(str_start) > 0:
        new_indent_level = indent_level + 1 if indent_adder else indent_level
        actual_docstrings = __format_complete_docstring(
            docstring_text[idx:], (new_indent_level, False)
        )[1]
        return ([docstring_text[:idx]], actual_docstrings, new_indent_level)
    if len(docstring_matches) > 1:
        docstring_contents = [
            match.group()[3:-3].strip() for match in docstring_matches
        ]
        docstring_contents = [text for text in docstring_contents if len(text) > 0]
        text = '"' * 3 + "\n\n".join(docstring_contents) + "\n" + '"' * 3
    else:
        text = docstring_matches[0].group().strip()
    return ([], __format_docstring(text), indent_level)


def get_formatted_docstring_script(script: str, line_length: int) -> str:
    """Returns a python script after reformatting its docstrings.

    This function reads a Python script, identifies all the docstrings, and formats them
    according to the specified line length and justification preferences. It returns the
    formatted script.

    Args:
        script (str): The Python script to format.
        line_length (int): The maximum length for each line in the formatted docstrings.

    Returns:
        str: The reformatted script.
    """
    script_lines = script.splitlines()
    docstrings_idx = __extract_docstrings(script)
    indentation_levels = __calculate_indentation_levels(script)
    for a, b in docstrings_idx[::-1]:
        prefix_docstring, docstring, actual_indentation = __format_complete_docstring(
            "\n".join(script_lines[a : b + 1]),
            indentation_levels[a + 1],
        )
        formatted_docstring = []
        if len(docstring) > 0:
            formatted_docstring = apply_google_style(
                lines=docstring,
                indentation_level=actual_indentation,
                line_length=line_length,
            )
        script_lines = (
            script_lines[:a]
            + prefix_docstring
            + formatted_docstring
            + script_lines[b + 1 :]
        )
    new_script = "\n".join([line.rstrip() for line in script_lines])
    while new_script[-1] == "\n" and len(new_script) > 0:
        new_script = new_script[:-1]
    new_script += "\n"
    return new_script


def format_script_docstrings(script_path: Path, line_length: int):
    """Format all the docstrings in a Python script to follow Google style guidelines.

    This  function  reads  a  Python  script from the specified path, identifies all the
    docstrings,   and   formats   them  according  to  the  specified  line  length  and
    justification  preferences.  After  formatting,  the  script  is  saved  back to the
    original file.

    Args:
        script_path (Path): The path to the Python script to format.
        line_length (int): The maximum length for each line in the formatted docstrings.

    Raises:
        FileNotFoundError: If  the  specified script file does not exist at the provided
            path.
    """
    if not script_path.is_file():
        abs_path = str(script_path.absolute())
        raise FileNotFoundError(f"File {abs_path} not found.")
    with script_path.open("r") as f:
        script = f.read()
    new_script = get_formatted_docstring_script(script, line_length)
    with script_path.open("w+") as f:
        f.write(new_script)
