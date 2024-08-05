from enum import Enum

class StrEnum(str, Enum):
    """
    StrEnum where enum.auto() returns the field name.
    See https://docs.python.org/3.9/library/enum.html#using-automatic-values
    """
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list) -> str:
        return name
        # Or if you prefer, return lower-case member (it's StrEnum default behavior since Python 3.11):
        # return name.lower()

    def __str__(self) -> str:
        # See https://peps.python.org/pep-0663/
        return self.value  # type: ignore
    
    
    @classmethod
    def to_dict(cls):
        """Returns a dictionary representation of the enum."""
        return {e.name: e.value for e in cls}
    
    @classmethod
    def keys(cls):
        """Returns a list of all the enum keys."""
        return cls._member_names_
    
    @classmethod
    def values(cls):
        """Returns a list of all the enum values."""
        return list(cls._value2member_map_.keys())