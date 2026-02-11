"""Secure shopping cart library with immutability and defensive programming."""

from .cart import ShoppingCart
from .catalog import Catalog, CatalogItem
from .exceptions import (
    CustomerIDValidationError,
    ImmutabilityViolationError,
    ItemNameValidationError,
    ItemNotInCartError,
    ItemNotInCatalogError,
    PriceValidationError,
    QuantityValidationError,
    ShoppingCartError,
    UUIDValidationError,
    ValidationError,
)
from .types import (
    MAX_ITEM_NAME_LENGTH,
    MAX_PRICE,
    MAX_QUANTITY,
    MIN_ITEM_NAME_LENGTH,
    MIN_PRICE,
    MIN_QUANTITY,
    PRICE_DECIMAL_PLACES,
    CartItems,
    ItemName,
    Price,
    Quantity,
)

__version__ = "1.0.0"

__all__ = [
    "ShoppingCart",
    "Catalog",
    "CatalogItem",
    "ShoppingCartError",
    "ValidationError",
    "CustomerIDValidationError",
    "QuantityValidationError",
    "ItemNameValidationError",
    "PriceValidationError",
    "UUIDValidationError",
    "ImmutabilityViolationError",
    "ItemNotInCatalogError",
    "ItemNotInCartError",
    "ItemName",
    "Quantity",
    "Price",
    "CartItems",
    "MIN_QUANTITY",
    "MAX_QUANTITY",
    "MIN_ITEM_NAME_LENGTH",
    "MAX_ITEM_NAME_LENGTH",
    "MIN_PRICE",
    "MAX_PRICE",
    "PRICE_DECIMAL_PLACES",
]
