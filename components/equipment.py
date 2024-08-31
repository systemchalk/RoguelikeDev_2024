"""Equipment confers lasting bonuses to entity.

Items are found in equippables.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    """Equipment occupies specific slots, conferring permanent bonuses."""

    parent: Actor

    def __init__(
            self, weapon: Item | None = None, armor: Item | None = None,
    ) -> None:
        """Assign status as weapon and/or armour."""
        self.weapon = weapon
        self.armor = armor

    @property
    def defense_bonus(self) -> int:
        """Amount of damage equipment prevents."""
        bonus = 0

        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.defense_bonus

        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.power_bonus

        return bonus

    @property
    def power_bonus(self) -> int:
        """Amount of damage equipment applies."""
        bonus = 0

        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.power_bonus

        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.power_bonus

        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        """Test if the item is equipped."""
        return item in (self.weapon, self.armor)

    def unequip_message(self, item_name: str) -> None:
        """Report an item is unequipped to the log."""
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}.",
        )

    def equip_message(self, item_name: str) -> None:
        """Report an item is equipped to the log."""
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}.",
        )

    def equip_to_slot(
            self, slot: str, item: Item, *, add_message: bool,
    ) -> None:
        """Equip an item, removing any existing equipment first."""
        current_item = getattr(self, slot)

        if current_item:
            self.unequip_from_slot(slot, add_message=add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, *, add_message: bool) -> None:
        """Remove an item from an equipment slot."""
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(
            self, equippable_item: Item, *, add_message: bool = True,
    ) -> None:
        """Switch equipment's status based on whether it is equipped or not."""
        if (
            equippable_item.equippable
            and (equippable_item.equippable.equipment_type
                 == EquipmentType.WEAPON)
        ):
            slot = "weapon"
        else:
            slot = "armor"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message=add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message=add_message)
