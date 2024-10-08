"""Game Map containing all the entities and traversable titles."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator

import numpy as np

import tile_types
from entity import Actor, Item

if TYPE_CHECKING:
    from tcod.console import Console

    from engine import Engine
    from entity import Entity


class GameMap:
    """GameMap of a given size containing entities."""

    def __init__(
        self, engine: Engine, width: int, height: int,
        entities: Iterable[Entity] = (),
    ) -> None:
        """Prepare a game map.

        Initialize a game map with an engine, width, height, a set of
        entities, and arrays of tiles, visible tiles, explored tiles, and a
        downstairs location.
        """
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full(
            (width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F",
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F",
        )  # Tiles the player has seen before
        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        """Return the GameMap."""
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        """Yield each of the items on the map."""
        yield from (entity
                    for entity
                    in self.entities
                    if isinstance(entity, Item)
                    )

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int,
    ) -> Entity | None:
        """Find the entity that is in the way at a given location."""
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Actor | None:
        """Get the actor at a given location."""
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """Render the map.

        If a tile is in the "visible" array, then draw it with the "light"
        colours. If it isn't, but it's in the "explored" array, then draw it
        with the "dark" colours. Otherwise, the default is "SHROUD".
        """
        console.rgb[0: self.width, 0: self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value,
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char,
                    fg=entity.color,
                )


class GameWorld:
    """Holds GameMap settings and generates new maps when moving downstairs."""

    def __init__(  # noqa: PLR0913
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            current_floor: int = 0,
    ) -> None:
        """Prepare a game world with GameMap defaults."""
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        """Generate a new dungeon floor."""
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )
