"""Equippables are the specific items that can be equipped.

Behaviours for equippables are found in equipment.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    """Equippables define specific equipment that can be equipped."""

    parent: Item

    def __init__(
            self,
            equipment_type: EquipmentType,
            power_bonus: int = 0,
            defense_bonus: int = 0,
    ) -> None:
        """Set up with equipment type, power_bonus, and defense_bonus."""
        self. equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus


class Dagger(Equippable):
    """Dagger is a weapon with attack 2."""

    def __init__(self) -> None:
        """Set up with attack 2."""
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)


class Sword(Equippable):
    """Sword is a weapon with attack 4."""

    def __init__(self) -> None:
        """Set up with attack 4."""
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)


class LeatherArmor(Equippable):
    """LeatherArmor is armour with defense 1."""

    def __init__(self) -> None:
        """Set up with defense 1."""
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)


class ChainMail(Equippable):
    """ChainMail is armour with defense 3."""

    def __init__(self) -> None:
        """Set up with defense 3."""
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)
