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


class Flake8ConfigNotFound(Exception):
    """
    Exception raised when valid flake8 configurations are not found in a TOML file.
    """


class InvalidFlake8PerFileIgnore(Exception):
    """
    Exception raised when an invalid per-file-ignore string is found in the TOML file.
    """
