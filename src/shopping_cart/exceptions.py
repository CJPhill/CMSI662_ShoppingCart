"""Custom exception hierarchy for the shopping cart library."""


class ShoppingCartError(Exception):
    """Base exception for all shopping cart errors."""

    pass


class ValidationError(ShoppingCartError):
    """Base exception for validation errors."""

    pass


class CustomerIDValidationError(ValidationError):
    """Invalid customer ID format."""

    pass


class QuantityValidationError(ValidationError):
    """Invalid quantity."""

    pass


class ItemNameValidationError(ValidationError):
    """Invalid item name."""

    pass


class PriceValidationError(ValidationError):
    """Invalid price."""

    pass


class UUIDValidationError(ValidationError):
    """Invalid UUID format."""

    pass


class ImmutabilityViolationError(ShoppingCartError):
    """Attempted modification of an immutable field."""

    pass


class ItemNotInCatalogError(ShoppingCartError):
    """Item does not exist in the catalog."""

    pass


class ItemNotInCartError(ShoppingCartError):
    """Item is not in the cart."""

    pass
