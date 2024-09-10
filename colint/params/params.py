from dataclasses import dataclass
from pathlib import Path

import toml

from .exceptions import (
    Flake8ConfigNotFound,
    IsortConfigNotFound,
    TomlNotFound,
    TomlNotValid,
)
from .flake8_params import Flake8Params
from .isort_params import IsortParams


@dataclass
class Params:
    """
    A class to hold parameters for tools.

    Attributes:
        isort (IsortParams): Holds isort configuration parameters.
        flake8 (Flake8Params): Holds flake8 configuration parameters.
    """

    isort: IsortParams
    flake8: Flake8Params

    @staticmethod
    def from_toml(toml_path: Path) -> "Params":
        """
        Static method to create Params instance from a TOML file.

        Args:
            toml_path (Path): Path to the TOML file.

        Returns:
            Params: An instance of Params class.

        Raises:
            TomlNotFound: If the TOML file does not exist.
            TomlNotValid: If the TOML file is not valid.
            IsortConfigNotFound: If 'isort' configuration is missing in the TOML file.
            Flake8ConfigNotFound: if 'flake8' configuration is missing in the TOML file.
        """
        try:
            data = toml.load(toml_path)
        except FileNotFoundError:
            raise TomlNotFound(f"{toml_path} is not a valid parameter file.")
        except toml.decoder.TomlDecodeError:
            raise TomlNotValid(f"{toml_path} does not exist.")

        data = data["tool"]

        if "isort" not in data.keys():
            raise IsortConfigNotFound(f"{toml_path} does not contain isort configurations.")
        if "flake8" not in data.keys():
            raise Flake8ConfigNotFound(f"{toml_path} does not contain flaek8 configurations.")

        return Params(isort=IsortParams.from_dict(data["isort"]), flake8=Flake8Params.from_dict(data["flake8"]))
