"""Actions define what entities can do in the game."""
from __future__ import annotations

from typing import TYPE_CHECKING

import color
import exceptions
from engine import Engine
from entity import Entity

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    """Base class for actions. Behaviour depends on specific action."""

    def __init__(self, entity: Actor) -> None:
        """Prepare an action with an entity."""
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self, engine: Engine, entity: Entity) -> None:
        """Perform this action with the objects needed to determine its scope.

        'self.engine' is the scope this action is being performed in.

        'self.entity' is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError


class ItemAction(Action):
    """Actions for items."""

    def __init__(
            self, entity: Actor, item: Item,
            target_xy: tuple[int, int] | None = None,
    ) -> None:
        """Initialize an ItemAction with an actor, item and optional target."""
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Actor | None:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the item's ability."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    """Drop an item."""

    def perform(self) -> None:
        """Remove an item if equipped, and drop it to the ground."""
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    """Equip/unequip an item, the opposite of its current status."""

    def __init__(self, entity: Actor, item: Item) -> None:
        """Initialize EquipAction with the item and entity."""
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        """Equip or unequip the item."""
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    """Not doing anything still takes a turn."""

    def perform(self) -> None:
        """Pass the turn."""
        pass  # noqa: PIE790


class TakeStairsAction(Action):
    """An action to change levels."""

    def perform(self) -> None:
        """Take the stairs, if any exist at the entity's location."""
        if ((self.entity.x, self.entity.y)
                == self.engine.game_map.downstairs_location):
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend,
            )
        else:
            msg = "There are no stairs here."
            raise exceptions.Impossible(msg)


class ActionWithDirection(Action):
    """A base class for actions that need to be performed in a direction."""

    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        """Initialize an ActionWithDirection with dx, dy values."""
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> tuple[int, int]:
        """Returns this action's destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        """Return the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at_location(
            *self.dest_xy)

    @property
    def target_actor(self) -> Actor | None:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        """Results depend on individual action."""
        raise NotImplementedError


class MeleeAction(ActionWithDirection):
    """Attack targets adjacent to entity."""

    def perform(self) -> None:
        """Damage target if it's valid."""
        target = self.target_actor
        if not target:
            msg = "Nothing to attack"
            raise exceptions.Impossible(msg)

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color,
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color,
            )


class MovementAction(ActionWithDirection):
    """Move or warn about impossible actions."""

    def perform(self) -> None:
        """Move to destination if not blocked."""
        dest_x, dest_y = self.dest_xy
        blocked_message = "That way is blocked."

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible(blocked_message)
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible(blocked_message)
        if self.engine.game_map.get_blocking_entity_at_location(dest_x,
                                                                dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible(blocked_message)

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    """Move in the direction or attack obstructing entities."""

    def perform(self) -> None:
        """Check if an entity is the way and attack, otherwise move."""
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        return MovementAction(self.entity, self.dx, self.dy).perform()


class PickupAction(Action):
    """Pick up an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor) -> None:
        """Initialize a PickupAction with an entity."""
        super().__init__(entity)

    def perform(self) -> None:
        """Add an item to the inventory or warn that inventory is full."""
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    msg = "Your inventory is full."
                    raise exceptions.Impossible(msg)

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(
                    f"You picked up the {item.name}!")
                return

        msg = "There is nothing here to pick up."
        raise exceptions.Impossible(msg)
