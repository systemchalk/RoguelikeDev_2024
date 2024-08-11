from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING, TypeVar

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """A generic object to represent players, enemies, items, etc."""

    parent: GameMap | Inventory

    def __init__(  # noqa: PLR0913
        self,
        parent: GameMap | None = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        *,
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ) -> None:
        """Initialize an Entity.

        Initalize an Entity with an optional parent, x and y coordinate,
        character representation, colour, name, blocks movement flag, and
        render order.
        """
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: GameMap | None = None) -> None:
        """Place this entity at a new location.

        Handles moving across GameMaps.
        """
        self.x = x
        self.y = y
        if gamemap:
            # Possibly uninitialized.
            if hasattr(self, "parent") and self.parent is self.gamemap:
                self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """Return the distance from the entity.

        Return the distance between the current entity and the given (x, y)
        coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class Actor(Entity):
    def __init__(  # noqa: PLR0913
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: type[BaseAI],
        fighter: Fighter,
        inventory: Inventory,
    ) -> None:
        """Initialize an Actor.

        Initializes an actor with x and y coordinates,
        character representation, colour, name, optional ai, fighter component
        and inventory. Ensures it can block and is rendered as an actor.
        """
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: BaseAI | None = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(  # noqa: PLR0913
            self,
            *,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            consumable: Consumable,
    ) -> None:
        """Initialize an item.

        Initialize an item with x and y coordinates, character representation,
        colour, name, and consumable. Ensures it cannot block the player and is
        rendered with the items.
        """
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable
        self.consumable.parent = self
