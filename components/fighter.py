"""Fighters are entities that can attack or be attacked."""
from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    """Fighters have health, attack, and defence and can take/give damage."""

    parent: Actor

    def __init__(self, hp: int, base_defense: int, base_power: int) -> None:
        """Initialize a Fighter with max_hp, current hp, defense, and power."""
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power

    @property
    def hp(self) -> int:
        """Get current hp."""
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        """Get current defence after bonuses."""
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        """Get current attack power after bonuses."""
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        """Get defence bonuses from any equipment."""
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        return 0

    @property
    def power_bonus(self) -> int:
        """Get attack power bonuses from any equipment."""
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        return 0

    def die(self) -> None:
        """Kill an entity if its health is 0.

        Death includes changing its representation and AI.
        """
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def heal(self, amount: int) -> int:
        """Heal HP by given amount up to max."""
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        new_hp_value = min(new_hp_value, self.max_hp)

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        """Reduce hp by given amount."""
        self.hp -= amount
