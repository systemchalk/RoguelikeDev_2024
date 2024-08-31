"""Engine keeps track of the state of the game."""
from __future__ import annotations

import contextlib
import lzma
import pickle
from pathlib import Path
from typing import TYPE_CHECKING

from tcod.map import compute_fov

import exceptions
import render_functions
from message_log import MessageLog

if TYPE_CHECKING:
    from tcod.console import Console

    from entity import Actor
    from game_map import GameMap, GameWorld


class Engine:
    """Engine keeps track of the map, world, and all entities within."""

    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor) -> None:
        """Intialize a GameMap.

        Initalize a GameMap with an empty message log, initial (0,0) mouse
        location, and player.
        """
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        """Each entity that isn't a player takes an action."""
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                with contextlib.suppress(exceptions.Impossible):
                    # Ignore impossible action exceptions from AI.
                    entity.ai.perform()

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored"
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        """Translate game data into visual on the screen."""
        self.game_map.render(console)

        self.message_log.render(console=console, x=21,
                                y=45, width=40, height=5)

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self,
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with Path(filename).open("wb") as f:
            f.write(save_data)
