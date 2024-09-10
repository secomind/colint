class TomlNotValid(Exception):
    """
    Exception raised when a Toml File is not valid.
    """


class TomlNotFound(Exception):
    """
    Exception raised when a configuration TOML file is not found.
    """


class IsortConfigNotFound(Exception):
    """
    Exception raised when valid isort configurations are not found in a TOML file.
    """

