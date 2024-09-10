class NotValidPath(Exception):
    """
    Custom error when the provided path is not a directory or a file
    """


class InvalidJupyterCellData(Exception):
    """
    Custom error raised when an invalid cell JSON is used to initialize JupyterCell class.
    """


class InvalidJupyterNotebookData(Exception):
    """
    Custom error raise when an invalid Jupyter Notebook JSON is used to initialize JupyterNoebookParser class.
    """
