"""Shopping cart with immutable IDs and defensive programming."""

import uuid
from copy import deepcopy
from decimal import Decimal
from typing import Any

from .catalog import Catalog
from .exceptions import (
    ImmutabilityViolationError,
    ItemNotInCartError,
    ItemNotInCatalogError,
)
from .types import CartItems, ItemName, Price, Quantity
from .validators import (
    validate_customer_id,
    validate_item_name,
    validate_quantity,
)


class ShoppingCart:
    """Secure shopping cart with immutable IDs, input validation, and defensive copying."""

    _IMMUTABLE_FIELDS = {"_cart_id", "_customer_id"}

    _cart_id: uuid.UUID
    _customer_id: str
    _catalog: Catalog
    _items: dict[ItemName, Quantity]

    def __init__(self, customer_id: str, catalog: Catalog) -> None:
        """Create a new cart for the given customer using the provided catalog."""
        if not isinstance(catalog, Catalog):
            raise TypeError(f"catalog must be a Catalog instance, got {type(catalog).__name__}")

        # Bypass __setattr__ override for initialization
        object.__setattr__(self, "_cart_id", uuid.uuid4())
        object.__setattr__(self, "_customer_id", validate_customer_id(customer_id))
        object.__setattr__(self, "_catalog", catalog)
        object.__setattr__(self, "_items", {})

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modification of immutable fields."""
        if name in self._IMMUTABLE_FIELDS:
            raise ImmutabilityViolationError(f"Cannot modify immutable field '{name.lstrip('_')}'")
        super().__setattr__(name, value)

    @property
    def cart_id(self) -> uuid.UUID:
        """Unique UUID4 identifier (immutable)."""
        return self._cart_id

    @property
    def customer_id(self) -> str:
        """Customer identifier (immutable)."""
        return self._customer_id

    def add_item(self, item_name: ItemName, quantity: Quantity) -> None:
        """Add an item to the cart, or increase quantity if already present."""
        item_name = validate_item_name(item_name)
        quantity = validate_quantity(quantity)

        if not self._catalog.has_item(item_name):
            raise ItemNotInCatalogError(f"Item '{item_name}' does not exist in the catalog")

        if item_name in self._items:
            new_quantity = validate_quantity(self._items[item_name] + quantity)
            self._items[item_name] = new_quantity
        else:
            self._items[item_name] = quantity

    def update_item_quantity(self, item_name: ItemName, quantity: Quantity) -> None:
        """Set the quantity of an existing cart item."""
        item_name = validate_item_name(item_name)
        quantity = validate_quantity(quantity)

        if item_name not in self._items:
            raise ItemNotInCartError(f"Item '{item_name}' is not in the cart")

        self._items[item_name] = quantity

    def remove_item(self, item_name: ItemName) -> None:
        """Remove an item from the cart."""
        item_name = validate_item_name(item_name)

        if item_name not in self._items:
            raise ItemNotInCartError(f"Item '{item_name}' is not in the cart")

        del self._items[item_name]

    def get_items(self) -> CartItems:
        """Get a defensive copy of all cart items."""
        return deepcopy(self._items)

    def get_total(self) -> Price:
        """Calculate the total cost of all items in the cart."""
        total = Decimal("0.00")

        for item_name, quantity in self._items.items():
            price = self._catalog.get_price(item_name)
            if price is not None:
                total += price * quantity

        return total
