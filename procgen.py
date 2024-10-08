"""Procedural generation of dungeons."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Iterator

import tcod

import entity_factories
import tile_types
from game_map import GameMap

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

item_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25),
        (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25),
        (entity_factories.chain_mail, 15)],
}

enemy_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}


def get_max_value_for_floor(
        weighted_chances_by_floor: list[tuple[int, int]], floor: int,
) -> int:
    """Return the maximum number of entities for a given floor."""
    current_value = 0

    for floor_minimum, value in weighted_chances_by_floor:
        if floor_minimum > floor:
            break
        current_value = value

    return current_value


def get_entities_at_random(
        weighted_chances_by_floor: dict[int, list[tuple[Entity, int]]],
        number_of_entities: int,
        floor: int,
) -> list[Entity]:
    """Get number_of_entities randomly selected entities based on the floor."""
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        for value in values:
            entity, weighted_chance = value

            entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    return random.choices(  # noqa: S311
        entities, weights=entity_weighted_chance_values, k=number_of_entities,
    )


class RectangularRoom:
    """Generic room and helpers to define size and intersection."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize a rectangular room.

        Intalize with x1 and y1 coordinates, and x2 width units from x1 and
        y2 height units from y1.
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        """Return the x and y coordinates of the center of the room."""
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(
    room: RectangularRoom, dungeon: GameMap, floor_number: int,
) -> None:
    """Randomly select a number of entities and place them in the room."""
    number_of_monsters = random.randint(0, get_max_value_for_floor(  # noqa: S311
        max_monsters_by_floor, floor_number))
    number_of_items = random.randint(0, get_max_value_for_floor(  # noqa: S311
        max_items_by_floor, floor_number))

    monsters: list[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number,
    )

    items: list[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number,
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)  # noqa: S311
        y = random.randint(room.y1 + 1, room.y2 - 1)  # noqa: S311

        if not any(entity.x == x and entity.y == y
                   for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def tunnel_between(
    start: tuple[int, int], end: tuple[int, int],
) -> Iterator[tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance  # noqa: PLR2004, S311
        # Move horizontally, then vertically
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(  # noqa: PLR0913
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: list[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)  # noqa: S311
        room_height = random.randint(room_min_size, room_max_size)  # noqa: S311

        x = random.randint(0, dungeon.width - room_width - 1)  # noqa: S311
        y = random.randint(0, dungeon.height - room_height - 1)  # noqa: S311

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue
        # If there are no intersections then the room is valid.abs

        # Dig out this room's inner area.abs
        dungeon.tiles[new_room.inner] = tile_types.floor

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        center_of_last_room = new_room.center

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        # Finally, append the new room to the list.
        rooms.append(new_room)

    return dungeon
