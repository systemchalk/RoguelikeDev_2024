"""Enum to establish the priority of rendering. Ascending importance."""
from enum import Enum, auto


class RenderOrder(Enum):
    """Enum to establish rendering order (Actor is highest)."""

    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
