"""AI classes to establish actor behaviour."""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np  # type : ignore
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    """Base AI class to specific types to inherit from."""

    entity: Actor

    def perform(self) -> None:
        """Perform should be defined by specific AI type."""
        raise NotImplementedError

    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an entity blocks movement and the cost isn't zero
            # (blocking).
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each
                # other in hallways. A higher number means enemies will take
                # longer paths in order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new
        # pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: list[list[int]] = pathfinder.path_to((dest_x, dest_y))[
            1:].tolist()

        # Convert from list List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """Confused enemies move randomly.

    A confused enemy will stumble around aimlessly for a given number of
    turns, then revert back to its previous AI. If an actor occupies a tile
    it is randomly moving into, it will attack.
    """

    def __init__(
            self, entity: Actor, previous_ai: BaseAI | None,
            turns_remaining: int,
    ) -> None:
        """Prepare a Confused enemy.

        Initialize a ConfusedEnemy with an entity, its previous AI (if any)
        and turns remaining for the effect.
        """
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        """Move randomly or restore old AI if the spell has worn off."""
        # Revert the AI back to its state if the effect has run its course
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused.",
            )
            self.entity.ai = self.previous_ai
            return None

        # Pick a random direction
        direction_x, direction_y = random.choice(  # noqa: S311
            [
                (-1, -1),  # Northwest
                (0, -1),  # North
                (1, -1),  # Northeast
                (-1, 0),  # West
                (1, 0),  # East
                (-1, 1),  # Southwest
                (0, 1),  # South
                (1, 1),  # Southeast
            ],
        )

        self.turns_remaining -= 1

        # The actor will try to move or attack in the chosen random
        # direction. It is possible the actor will just bump into the
        # wall, wasting a turn.
        return BumpAction(self.entity, direction_x, direction_y).perform()


class HostileEnemy(BaseAI):
    """Standard enemies that chase after the player after detection."""

    def __init__(self, entity: Actor) -> None:
        """Initialize a HostileEnemy with an entity and an empty path."""
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self) -> None:
        """Attack the player or chase down the detected player if too far."""
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()
