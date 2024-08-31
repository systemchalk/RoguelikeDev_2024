"""Consumable items."""
from __future__ import annotations

from typing import TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    """Consumables perform actions and then are destroyed."""

    parent: Item

    def get_action(self, consumer: Actor) -> ActionOrHandler | None:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this item's ability.

        'action' is the context for this activation.
        """
        raise NotImplementedError

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class ConfusionConsumable(Consumable):
    """ConfusionConsumables apply confusion to targets."""

    def __init__(self, number_of_turns: int) -> None:
        """Initialize a ConfusionConsumable with a number of turns."""
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> ActionOrHandler | None:
        """Prompt the player for a target to confuse."""
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target,
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        """Check if the target is valid and confuse it."""
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            msg = "You cannot target an area that you cannot see."
            raise Impossible(msg)
        if not target:
            msg = "You must select an enemy to target"
            raise Impossible(msg)
        if target is consumer:
            msg = "You cannot confuse yourself!"
            raise Impossible(msg)

        self.engine.message_log.add_message(
            f"The eyes of the {
                target.name} look vacant, as it start to stumble around!",
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai,
            turns_remaining=self.number_of_turns,
        )
        self.consume()


class HealingConsumable(Consumable):
    """HealingConsumables heal the owner and are destroyed."""

    def __init__(self, amount: int) -> None:
        """Prepare a HealingConsumable with amount of HP restored."""
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        """Check if the consumer is wounded and heal."""
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {
                    amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            msg = "Your health is already full."
            raise Impossible(msg)


class FireballDamageConsumable(Consumable):
    """Fireballs deal targeted area of effect damage before being destroyed."""

    def __init__(self, damage: int, radius: int) -> None:
        """Prepare a FireballDamageConsumable with damage and radius."""
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        """Prompt the player for the target."""
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target,
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        """Check if the target is valid and apply damage."""
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            msg = "You cannot target an area that you cannot see."
            raise Impossible(msg)

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {
                        actor.name} is engulfed in a fiery explosion, taking {
                        self.damage} damage!",
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            msg = "There are no targets in the radius."
            raise Impossible(msg)
        self.consume()


class LightningDamageConsumable(Consumable):
    """LightnightDamageConsumable deals direct damage, ignoring armour."""

    def __init__(self, damage: int, maximum_range: int) -> None:
        """Prepare a LightningDamageConsumable with damage and max range."""
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        """Damage the closest enemy or warn if none are available."""
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if (actor is not consumer
                    and self.parent.gamemap.visible[actor.x, actor.y]):
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lightning bolt strikes the {
                    target.name} with a loud thunder, for {
                        self.damage} damage!",
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            msg = "No enemy is close enough to strike."
            raise Impossible(msg)
