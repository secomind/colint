import re
from dataclasses import dataclass, field

from .format_text import format_text_with_prefix


@dataclass
class ListElement:
    """Represents a list element in a formatted docstring.

    A  list  element  consists  of  a  heading  and line. Heading is whatever is used to
    introduce  the  element.  For example, it could be a symbol (e.g. "7-"), or a number
    (e.g.  "7.") or even the name of a variable with its typing (e.g. "heading (str)" as
    below). Lines is the element actual content.

    Attributes:
        heading (str): The heading of the element.
        lines (list[str]): The content lines after the element heading.
    """

    heading: str = ""
    lines: list[str] = field(default_factory=lambda: [])


@dataclass
class Section:
    """Represents a section in a formatted docstring.

    A  section  can  possibly contain a heading, a list of content lines, and possibly a
    list of subsections.

    Attributes:
        title_summary_section (bool): Indicates  if  this  section contains the title or
            summary.
        lines (list[str]): The main content lines of the section.
        heading (str | None): The  heading  for  the section (if applicable).Not used if
            title_summary_section is True.
        list_elements (list[ListElement]): The  elements within the section. Not used if
            title_summary_section is True.
    """

    title_summary_section: bool = True
    lines: list[str] = field(default_factory=lambda: [])
    heading: str | None = None
    list_elements: list[ListElement] = field(default_factory=lambda: [])


__google_docs_section_keys = [
    "Args",
    "Returns",
    "Raises",
    "Attributes",
    "Yields",
    "Examples",
    "See Also",
    "Notes",
    "Warnings",
    "References",
    "Deprecated",
    "TODO",
]

__google_docs_section_patterns = [
    re.compile(f"^{s}\\s*:$", re.IGNORECASE) for s in __google_docs_section_keys
]


def __get_google_doc_heading(line: str) -> str | None:
    """Returns heading if the given line matches a Google-style docstring heading.

    Args:
        line (str): A single line from the docstring.

    Returns:
        str | None: The matched section heading if found, otherwise None.
    """
    idx = -1
    for k, pattern in enumerate(__google_docs_section_patterns):
        if pattern.match(line.strip()):
            idx = k
            break
    if idx < 0:
        return None
    return f"{__google_docs_section_keys[idx]}:"


__parameter_pattern = re.compile(r"^\*{0,2}\w+\s*(\([^)]*\))?\s*:")
__datatype_pattern = re.compile(r"^\w+\s*(\[[^)]*\])?\s*:")
__list_element_pattern = re.compile(r"^(-|\d+\.)")


def __is_parameter_explaining(line: str) -> tuple[str | None, str | None]:
    """Identifies whether a line in the docstring is a list element.

    Args:
        line (str): A single line from the docstring.

    Returns:
        tuple[str | None, str | None]: The list element heading and the rest of the line
            text (if any), otherwise (None, None).
    """
    line = line.strip()
    match = __parameter_pattern.match(line)
    if match:
        value = match.group()[:-1].strip()
        value = " ".join(value.split())
        value += ":"
        return value, line[match.end() :].strip()
    match = __datatype_pattern.match(line)
    if match:
        value = match.group()[:-1].strip()
        if "[" in value:
            name = value.split("[")[0].strip()
            value = name + value[len(name) :].strip()
        value += ":"
        return value, line[match.end() :].strip()
    match = __list_element_pattern.match(line)
    if match:
        return match.group().strip(), line[match.end() :].strip()
    return None, None


def __divide_into_sections(lines: list[str]) -> list[Section]:
    """Divides the docstring lines into sections and subsections.

    Args:
        lines (list[str]): The lines from the docstring.

    Returns:
        list[Section]: A  list  of  Section  objects,  each  containing  its  own lines,
            heading, and any subsections.
    """
    current_section = Section()
    sections: list[Section] = []
    for line in lines:
        if len(line.strip()) == 0:
            sections.append(current_section)
            current_section = Section()
            continue
        heading = __get_google_doc_heading(line)
        if heading:
            sections.append(current_section)
            current_section = Section(title_summary_section=False, heading=heading)
            continue
        if current_section.title_summary_section:
            current_section.lines.append(line)
            continue
        heading, rest_of_line = __is_parameter_explaining(line)
        if heading is None or rest_of_line is None:
            if len(current_section.list_elements) == 0:
                current_section.lines.append(line)
            else:
                current_section.list_elements[-1].lines.append(line)
        else:
            current_section.list_elements.append(
                ListElement(heading=heading, lines=[rest_of_line])
            )
    sections.append(current_section)
    return [s for s in sections if len(s.lines) > 0 or s.heading is not None]


def __single_line_docstring(
    lines: list[str],
    indentation_level: int,
) -> str:
    """Formats the docstring lines into a single line string.

    Args:
        lines (list[str]): The lines of the docstring.
        indentation_level (int): The  level  of indentation (each level corresponds to 4
            spaces).

    Returns:
        str: A single-line docstring string.
    """
    text = "\n".join(lines)
    text = text.rstrip().rstrip('"')
    words = text.split()
    words[-1] += '"""'
    indent = " " * indentation_level * 4
    return indent + " ".join(words)


def apply_google_style(
    lines: list[str], indentation_level: int, line_length: int
) -> list[str]:
    """Applies Google-style formatting to the given docstring lines.

    Args:
        lines (list[str]): The raw lines of the docstring to format.
        indentation_level (int): The level of indentation (4 spaces per level).
        line_length (int): The maximum length of each line.

    Returns:
        list[str]: A   list   of   formatted   docstring  lines  following  Google-style
            formatting.
    """
    single_line_comment = __single_line_docstring(lines, indentation_level)
    has_multiple_periods = "." in single_line_comment.rstrip('"').rstrip().rstrip(".")
    if len(single_line_comment) <= line_length and not has_multiple_periods:
        return [single_line_comment]
    lines = lines[:-1]
    sections = __divide_into_sections(lines)
    result = []
    normal_indent = " " * indentation_level * 4
    first_indent = normal_indent + " " * 4
    second_indent = first_indent + " " * 4
    for section in sections:
        if section.title_summary_section:
            result += format_text_with_prefix(
                text="\n".join(section.lines),
                prefix=normal_indent,
                line_length=line_length,
            )
            result.append("")
            continue
        result.append(f"{normal_indent}{section.heading.strip()}")
        result += format_text_with_prefix(
            text="\n".join(section.lines),
            prefix=first_indent,
            line_length=line_length,
        )
        for element in section.list_elements:
            element_text = "\n".join(element.lines)
            first_line = format_text_with_prefix(
                text=element_text,
                prefix=first_indent + element.heading + " ",
                line_length=line_length,
            )[0]
            result.append(first_line)
            words = first_line.strip()[len(element.heading) :].split()
            all_words = element_text.split()
            text_remaining = " ".join(all_words[len(words) :])
            other_lines = format_text_with_prefix(
                text=text_remaining,
                prefix=second_indent,
                line_length=line_length,
            )
            result += other_lines
        result.append("")
    while result[-1] == "":
        result.pop()
    result.append(f'{normal_indent}"""')
    return result
