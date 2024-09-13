from dataclasses import dataclass, field

from .exceptions import InvalidFlake8PerFileIgnore


@dataclass
class Flake8Params:
    """
    A data class to represent Flake8 configuration parameters.

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

    @staticmethod
    def from_dict(obj: dict) -> "Flake8Params":
        """
        Create a Flake8Params instance from a dictionary.

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

        try:
            max_complexity = int(obj.get("max-complexity", -1))
        except ValueError:
            max_complexity = -1

        try:
            quiet = int(obj.get("quiet", 2))
        except ValueError:
            quiet = 2

        return Flake8Params(
            per_file_ignores=per_file_ignores, extend_ignore=extend_ignore, max_complexity=max_complexity, quiet=quiet
        )
