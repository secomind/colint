from dataclasses import dataclass, field


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

    target_version: list[str] = field(default_factory=lambda: ["py10"])
    line_length: int = 88
    preview: bool = False
    unstable: bool = False

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

        return BlackParams(target_version=versions, line_length=line_length, preview=preview, unstable=unstable)
