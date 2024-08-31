"""Base component to be added to entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap


class BaseComponent:
    """BaseComponents are attached to entities to add capabilities."""

    parent: Entity  # Owning entity instance.

    @property
    def gamemap(self) -> GameMap:
        """The entity's GameMap."""
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        """The entity's engine (via GameMap)."""
        return self.gamemap.engine
