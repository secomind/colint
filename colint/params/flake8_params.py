from dataclasses import dataclass, field

from .exceptions import InvalidFlake8PerFileIgnore


@dataclass
class Flake8Params:
    """A data class to represent Flake8 configuration parameters.

    Attributes:
        per_file_ignores (dict[str, list[str]]): A dictionary to specify errors to ignore for specific files.
        extend_ignore (list[str]): A list of error codes to extend the default ignore list.
        max_complexity (int): The maximum allowed complexity for the code.
        quiet (int): The quiet level for Flake8 (controls verbosity).
    """

    per_file_ignores: dict[str, list[str]] = field(default_factory=dict)
    extend_ignore: list[str] = field(default_factory=list)
    max_complexity: int = -1
    quiet: int = 2
    docstring_convention: str = "pep257"

    @staticmethod
    def __safe_get_integer(obj: dict, key: str, default_value: int) -> int:
        """Safely retrieves an integer value from a dictionary by key.

        This function attempts to retrieve the value associated with the specified
        key from the given dictionary and convert it to an integer. If the key
        does not exist, or if the conversion fails due to a ValueError, it returns
        the provided default value.

        Args:
            obj (dict): The dictionary from which to retrieve the value.
            key (str): The key whose corresponding value is to be retrieved.
            default_value (int): The default value to return if the key is not found
                or the value cannot be converted to an integer.

        Returns:
            int: The integer value corresponding to the specified key, or the default
            value if the key is not found or conversion fails.
        """
        try:
            return int(obj.get(key, default_value))
        except ValueError:
            return default_value

    @staticmethod
    def from_dict(obj: dict) -> "Flake8Params":
        """Create a Flake8Params instance from a dictionary.

        Args:
            obj (dict): A dictionary containing Flake8 configuration parameters.

        Returns:
            Flake8Params: An instance of Flake8Params.

        Raises:
            InvalidFlake8PerFileIgnore: If the per-file-ignore property is improperly formatted.
        """
        per_file_ignores_string = obj.get("per-file-ignores")
        if not isinstance(per_file_ignores_string, str):
            per_file_ignores_string = ""
        per_file_ignores = {}
        for line in per_file_ignores_string.splitlines():
            if len(line.strip()) == 0:
                continue
            try:
                fname, errors = line.split(":")
            except ValueError:
                raise InvalidFlake8PerFileIgnore("Invalid per-file-ignore property.")
            per_file_ignores[fname.strip()] = [err.strip() for err in errors.split(",")]

        extend_ignore = obj.get("extend-ignore")
        if not isinstance(extend_ignore, list):
            extend_ignore = []

        max_complexity = Flake8Params.__safe_get_integer(obj, "max-complexity", -1)
        quiet = Flake8Params.__safe_get_integer(obj, "quiet", 2)

        docstring_convention = obj.get("docstring-convention", "pep257")

        return Flake8Params(
            per_file_ignores=per_file_ignores,
            extend_ignore=extend_ignore,
            max_complexity=max_complexity,
            quiet=quiet,
            docstring_convention=docstring_convention,
        )
