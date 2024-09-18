from dataclasses import dataclass, field

from black.mode import TargetVersion

_str_to_target_version = {
    "py3": TargetVersion.PY33,
    "py4": TargetVersion.PY34,
    "py5": TargetVersion.PY35,
    "py6": TargetVersion.PY36,
    "py7": TargetVersion.PY37,
    "py8": TargetVersion.PY38,
    "py9": TargetVersion.PY39,
    "py10": TargetVersion.PY310,
    "py11": TargetVersion.PY311,
    "py12": TargetVersion.PY312,
    "py13": TargetVersion.PY313,
}


@dataclass
class BlackParams:
    """
    A data class to represent Black configuration parameters.

    Attributes:
        target_version (list[str]): List of target Python versions for the Black formatter.
        line_length (int): Maximum allowed line length.
        preview (bool): Whether to enable preview features.
        unstable (bool): Whether to enable unstable features.
    """

    target_version: set[TargetVersion] = field(
        default_factory=lambda: {TargetVersion.PY310}
    )
    line_length: int = 88
    preview: bool = False
    unstable: bool = False

    @staticmethod
    def convert_to_target_version(key: str) -> TargetVersion:
        if key not in _str_to_target_version:
            raise KeyError(f"Unsupported target version: {key}.")
        return _str_to_target_version[key]

    @staticmethod
    def from_dict(obj: dict) -> "BlackParams":
        """
        Create a BlackParams instance from a dictionary.

        Args:
            obj (dict): A dictionary containing Black configuration parameters.

        Returns:
            BlackParams: An instance of BlackParams.
        """
        versions = obj.get("target-version", ["py10"])
        if isinstance(versions, str):
            versions = [versions]
        versions = set(_str_to_target_version[k] for k in versions)

        try:
            line_length = int(obj.get("line_length", 88))
        except ValueError:
            line_length = 88

        try:
            preview = bool(obj.get("preview", False))
        except:
            preview = False

        try:
            unstable = bool(obj.get("unstable", False))
        except:
            unstable = False

        return BlackParams(
            target_version=versions,
            line_length=line_length,
            preview=preview,
            unstable=unstable,
        )
