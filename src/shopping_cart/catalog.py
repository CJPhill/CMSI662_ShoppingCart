"""Immutable product catalog with defensive copying."""

from copy import deepcopy
from dataclasses import dataclass

from .types import ItemName, Price
from .validators import validate_item_name, validate_price


@dataclass(frozen=True)
class CatalogItem:
    """Immutable catalog item with validated name and price."""

    name: ItemName
    price: Price

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        object.__setattr__(self, "name", validate_item_name(self.name))
        object.__setattr__(self, "price", validate_price(self.price))


class Catalog:
    """Read-only product catalog. Returns defensive copies to prevent modification."""

    def __init__(self, items: dict[ItemName, Price]) -> None:
        """Initialize catalog with a dict of item names to prices."""
        self._items: dict[ItemName, CatalogItem] = {
            name: CatalogItem(name=name, price=price) for name, price in items.items()
        }

    def has_item(self, item_name: ItemName) -> bool:
        """Check if an item exists in the catalog."""
        return item_name in self._items

    def get_price(self, item_name: ItemName) -> Price | None:
        """Get the price of an item, or None if not found."""
        item = self._items.get(item_name)
        return item.price if item else None

    def get_all_items(self) -> dict[ItemName, Price]:
        """Get a defensive copy of all items."""
        return deepcopy({name: item.price for name, item in self._items.items()})
