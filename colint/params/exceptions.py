class TomlNotValid(Exception):
    """Toml not valid.

    Exception raised when a Toml File is not valid.

    """


class TomlNotFound(Exception):
    """Toml not found.

    Exception raised when a configuration TOML file is not found.
    """


class IsortConfigNotFound(Exception):
    """Isort config not found.

    Exception raised when valid isort configurations are not found in a TOML file.
    """


class Flake8ConfigNotFound(Exception):
    """Flake8 config not found.

    Exception raised when valid flake8 configurations are not found in a TOML file.
    """


class InvalidFlake8PerFileIgnore(Exception):
    """Invalid Flake8 per file ignore.

    Exception raised when an invalid per-file-ignore string is found in the TOML file.
    """


class BlackConfigNotFound(Exception):
    """Black config not found.

    Exception raised when valid flake8 configurations are not found in a TOML file.
    """
