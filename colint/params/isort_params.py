from dataclasses import dataclass


@dataclass
class IsortParams:
    """
    A class to represent isort parameters.

    Attributes:
        profile (str | None): Isort configuration profile.
    """

    profile: str | None

    @staticmethod
    def from_dict(obj: dict) -> "IsortParams":
        return IsortParams(profile=obj.get("profile"))
