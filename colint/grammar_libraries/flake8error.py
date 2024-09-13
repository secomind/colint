from pathlib import Path

from ..utils.text_formatting_utils import TextModifiers, format_text


class Flake8Error:
    """
    A class to represent a Flake8 error and provide methods for formatting
    and determining if it should be ignored.

    Attributes:
        code (str): The error code.
        line_number (int): The line number where the error occurred.
        col_number (int): The column number where the error occurred.
        message (str): The error message.
        cell_number (int | None): The cell number (used in jupyter noteboks contexts).
        filename (str): The name of the file where the error occurred.
    """

    def __init__(self, fname: str, error_tuple: tuple[str, int, int, str, str]) -> None:
        """
        Initialize a Flake8Error instance.

        Args:
            fname (str): The filename where the error occurred.
            error_tuple (tuple[str, int, int, str, str]): A tuple containing the error code, line number,
                                                          column number, message, and a placeholder.
        """
        self.code, self.line_number, self.col_number, self.message, _ = error_tuple
        self.filename = fname
        self.cell_number = None

    def to_str(self) -> str:
        """
        Convert the Flake8Error instance to a formatted string.

        Returns:
            str: A string representation of the Flake8 error with formatting.
        """
        cell_format_list = []
        if self.cell_number:
            cell_format_list = [format_text(f"Cell{self.cell_number}", TextModifiers.INVERSE)]
        path_formatted = ":".join(
            [str(Path(self.filename).resolve())] + cell_format_list + [str(self.line_number), str(self.col_number)]
        )
        code_formatted = format_text(self.code, [TextModifiers.ERROR, TextModifiers.BOLD])
        return f"{code_formatted} {path_formatted} - {self.message}"

    def should_be_ignored(self, ignore: list[str] = [], per_file_ignores: dict[str, list[str]] = {}) -> bool:
        """
        Determine whether the Flake8Error should be ignored based on the provided ignore lists.

        Args:
            ignore (list[str], optional): A list of codes to be ignored globally. Defaults to [].
            per_file_ignores (dict[str, list[str]], optional): A dictionary mapping filenames to lists of
                                                               codes to ignore for those specific files.
                                                               Defaults to {}.

        Returns:
            bool: True if the error should be ignored, False otherwise.
        """
        to_ignore = ignore.copy()

        file_path = Path(self.filename)
        if not file_path.is_file():
            return True

        basename = file_path.name

        if basename in per_file_ignores:
            to_ignore += per_file_ignores[basename]

        return any([self.code.startswith(ignored_code) for ignored_code in to_ignore])
