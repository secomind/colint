from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class IsortParams:
    """A class to represent isort parameters.

    Attributes:
        profile (str | None): Isort configuration profile which determines the
            formatting rules to be applied.
    """

    profile: Union[str, None]

    @staticmethod
    def from_dict(obj: Dict[str, Union[str, None]]) -> "IsortParams":
        """Create an instance of IsortParams from a dictionary.

        This method extracts the 'profile' key from the given dictionary and
        uses it to initialize an IsortParams instance.

        Args:
            obj (dict): A dictionary containing the parameters for isort.
                It expects a key 'profile' with a string value or None.

        Returns:
            IsortParams: An instance of the IsortParams class initialized with
            the provided parameters.
        """
        return IsortParams(profile=obj.get("profile"))
