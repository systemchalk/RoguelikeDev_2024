"""Equipment_types is an enum to define equipment types."""
from enum import Enum, auto


class EquipmentType(Enum):
    """What kind of equipment you have."""

    WEAPON = auto()
    ARMOR = auto()
