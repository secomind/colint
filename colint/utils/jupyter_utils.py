import json
from pathlib import Path

from .exceptions import InvalidJupyterCellData, InvalidJupyterNotebookData


def delete_from_dict_if_exists(d: dict, keys: list[str]):
    """
    Remove specified keys from a dictionary if they exist.

    Args:
        d (dict): The dictionary to remove keys from.
        keys (list[str]): The list of keys to remove.

    Returns:
        dict: A new dictionary with the specified keys removed.
    """
    res = d.copy()
    for key in [k for k in keys if k in d.keys()]:
        del res[key]
    return res


def safe_json_load(path: Path):
    text = path.read_text().strip()
    if len(text) == 0:
        return None
    return json.loads(text)


class JupyterCell:
    """
    Representation of a Jupyter notebook cell.

    Attributes:
        __cell_type (str): The type of the cell ('code', 'markdown', 'raw').
        __lines (list[str]): The source code/text of the cell.
        __outputs (list[dict]): The outputs of the cell if it's a code cell.
        __execution_count (int or None): The execution count of the cell if it's a code cell.
        __metadata (dict): Additional metadata for the cell.
    """

    def __init__(self, cell_data: dict):
        """
        Initialize a JupyterCell with given cell data.

        Args:
            cell_data (dict): The data representing a Jupyter notebook cell.

        Raises:
            InvalidJupyterCellData: If essential keys are missing from cell data.
        """
        try:
            self.__cell_type = cell_data["cell_type"]
        except KeyError:
            raise InvalidJupyterCellData("Invalid cell found")
        try:
            self.__lines = cell_data["source"]
        except KeyError:
            raise InvalidJupyterCellData("Invalid cell found")
        self.__outputs = []
        self.__execution_count = None
        if self.__cell_type == "code":
            try:
                self.__outputs = cell_data["outputs"]
                self.__execution_count = cell_data.get("execution_count")
            except KeyError:
                raise InvalidJupyterCellData("Invalid cell found")
        self.__metadata = delete_from_dict_if_exists(
            cell_data, ["cell_type", "source", "outputs", "execution_count"]
        )

    @property
    def text(self):
        """
        Get the text of the cell.

        Returns:
            str: The text of the cell joined by newline characters.
        """
        return "".join(self.__lines)

    @text.setter
    def text(self, value: str):
        """
        Set the text of the cell.

        Args:
            value (str): The text to set for the cell.
        """
        self.__lines = [line + "\n" for line in value.splitlines()]

    @property
    def cell_type(self):
        """
        Get the type of the cell.

        Returns:
            str: The type of the cell.
        """
        return self.__cell_type

    @property
    def size(self):
        """
        Get the number of lines in the cell.

        Returns:
            int: The number of lines in the cell.
        """
        return len(self.__lines)

    @property
    def execution_count(self):
        """
        Get the execution count of the cell.

        Returns:
            int or None: The execution count of the cell if it's a code cell, otherwise None.
        """
        return self.__execution_count

    def has_code(self) -> bool:
        """
        Check if there is any code in the cell (excluding comments and empty lines).

        Returns:
            bool: True if there is any code, False otherwise.
        """
        if self.__cell_type != "code":
            return False
        return any(
            [
                len(line.strip()) > 0 and not line.strip().startswith("#")
                for line in self.__lines
            ]
        )

    def has_output(self, picky: bool = False) -> bool:
        """
        Check if the cell has any outputs.

        Args:
            picky (bool): Whether to consider a non-null execution count as an output. Defaults to False.

        Returns:
            bool: True if there are outputs, False otherwise.
        """
        return (len(self.__outputs) > 0) or (
            picky and self.__execution_count is not None
        )

    def clear_output(self, reset_execution_count: bool = False):
        """
        Clear all outputs from the cell.

        Args:
            reset_execution_count (bool): Whether to reset the execution count to None. Defaults to False.
        """
        self.__outputs = []
        if reset_execution_count:
            self.__execution_count = None

    def to_dict(self) -> dict:
        """
        Convert the cell to a dictionary.

        Returns:
            dict: A dictionary representation of the cell.
        """
        res = self.__metadata.copy()
        res["cell_type"] = self.__cell_type
        res["source"] = self.__lines
        if self.__cell_type == "code":
            res["outputs"] = self.__outputs
            res["execution_count"] = self.__execution_count
        return res


class JupyterNotebokParser:
    """
    Parser for Jupyter notebook files.

    Attributes:
        __cells (list[JupyterCell]): List of cells in the notebook.
        __metadata (dict): Additional metadata for the notebook.
    """

    def __init__(self, path: Path | str) -> None:
        """
        Initialize the parser with the path to a Jupyter notebook file.

        Args:
            path (Path | str): The path to the Jupyter notebook file.

        Raises:
            FileNotFoundError: If the file does not exist.
            InvalidJupyterNotebookData: If 'cells' key is missing in the notebook data.
        """
        nb_path = Path(path)
        if not nb_path.is_file():
            raise FileNotFoundError(f"File {str(path)} does not exist.")
        data = safe_json_load(nb_path)
        if data is None:
            self.__cells = []
            self.__metadata = dict()
            return
        if "cells" not in data.keys():
            raise InvalidJupyterNotebookData("Cannot found 'cells' in Jupyter data.")
        self.__cells = [JupyterCell(c) for c in data["cells"]]
        self.__metadata = delete_from_dict_if_exists(data, ["cells"])

    def cells(self):
        """
        Generator that yields all cells in the notebook.

        Yields:
            JupyterCell: Each cell in the notebook.
        """
        for cell in self.__cells:
            yield cell

    def code_cells(self, exclude_empty: bool = False):
        """
        Generator that yields code cells in the notebook.

        Args:
            exclude_empty (bool): If True, excludes cells that don't have code. Defaults to False.

        Yields:
            JupyterCell: Each code cell in the notebook that meets the criteria.
        """
        for cell in self.__cells:
            if cell.cell_type != "code":
                continue
            if not exclude_empty or cell.has_code():
                yield cell

    def markdown_cells(self):
        """
        Generator that yields markdown cells in the notebook.

        Yields:
            JupyterCell: Each markdown cell in the notebook.
        """
        for cell in self.__cells:
            if cell.cell_type == "markdown":
                yield cell

    def to_dict(self) -> dict:
        """
        Convert the notebook to a dictionary.

        Returns:
            dict: A dictionary representation of the notebook.
        """
        res = self.__metadata.copy()
        res["cells"] = [c.to_dict() for c in self.__cells]
        return res

    def save(self, fname: Path | str):
        """
        Save the notebook to a file.

        Args:
            fname (Path | str): The path to the file where the notebook will be saved.
        """
        with Path(fname).open("w") as fp:
            json.dump(self.to_dict(), fp)
