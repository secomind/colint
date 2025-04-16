class NotValidPath(Exception):
    """Not valid path.

    Custom error when the provided path is not a directory or a file.
    """


class InvalidJupyterCellData(Exception):
    """Invalid Jupyter cell data.

    Custom error raised when an invalid cell JSON
    is used to initialize JupyterCell class.
    """


class InvalidJupyterNotebookData(Exception):
    """Invalid Jupyter notebook data.

    Custom error raise when an invalid Jupyter Notebook JSON
    is used to initialize JupyterNoebookParser class.
    """
