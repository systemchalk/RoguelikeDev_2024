"""Inventory stores any items picked up."""
from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    """Inventory adds capacity for items and ability to drop them."""

    parent: Actor

    def __init__(self, capacity: int) -> None:
        """Initialize an inventory with capacity and an empty list of items."""
        self.capacity = capacity
        self.items: list[Item] = []

    def drop(self, item: Item) -> None:
        """Drop an item to the game map.

        Remove an item from the inventory and restore it to the game map, at
        the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}")
