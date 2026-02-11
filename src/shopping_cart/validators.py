"""Input validation for the shopping cart library."""

import re
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any

from .exceptions import (
    CustomerIDValidationError,
    ItemNameValidationError,
    PriceValidationError,
    QuantityValidationError,
    UUIDValidationError,
)
from .types import (
    CUSTOMER_ID_PATTERN,
    ITEM_NAME_PATTERN,
    MAX_ITEM_NAME_LENGTH,
    MAX_PRICE,
    MAX_QUANTITY,
    MIN_ITEM_NAME_LENGTH,
    MIN_PRICE,
    MIN_QUANTITY,
    PRICE_DECIMAL_PLACES,
)

_CUSTOMER_ID_REGEX = re.compile(CUSTOMER_ID_PATTERN)
_ITEM_NAME_REGEX = re.compile(ITEM_NAME_PATTERN)


def _contains_null_bytes(value: str) -> bool:
    """Check if string contains null bytes."""
    return "\x00" in value


def _contains_control_characters(value: str) -> bool:
    """Check if string contains ASCII control characters (except newline/tab)."""
    return any(ord(c) < 32 and c not in "\n\t" for c in value)


def validate_customer_id(customer_id: Any) -> str:
    """Validate customer ID matches format XXX#####XX-[A|Q]."""
    if not isinstance(customer_id, str):
        raise CustomerIDValidationError(
            f"Customer ID must be a string, got {type(customer_id).__name__}"
        )

    if _contains_null_bytes(customer_id):
        raise CustomerIDValidationError("Customer ID contains null bytes")

    if _contains_control_characters(customer_id):
        raise CustomerIDValidationError("Customer ID contains control characters")

    if not _CUSTOMER_ID_REGEX.match(customer_id):
        raise CustomerIDValidationError(
            f"Customer ID '{customer_id}' does not match required format: XXX#####XX-[A|Q]"
        )

    return customer_id


def validate_quantity(quantity: Any) -> int:
    """Validate quantity is an integer between MIN_QUANTITY and MAX_QUANTITY."""
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise QuantityValidationError(f"Quantity must be an integer, got {type(quantity).__name__}")

    if quantity < MIN_QUANTITY:
        raise QuantityValidationError(f"Quantity must be at least {MIN_QUANTITY}, got {quantity}")

    if quantity > MAX_QUANTITY:
        raise QuantityValidationError(f"Quantity cannot exceed {MAX_QUANTITY}, got {quantity}")

    return quantity


def validate_item_name(item_name: Any) -> str:
    """Validate item name is 1-100 chars, alphanumeric/spaces/hyphens only."""
    if not isinstance(item_name, str):
        raise ItemNameValidationError(f"Item name must be a string, got {type(item_name).__name__}")

    if _contains_null_bytes(item_name):
        raise ItemNameValidationError("Item name contains null bytes")

    if _contains_control_characters(item_name):
        raise ItemNameValidationError("Item name contains control characters")

    if len(item_name) < MIN_ITEM_NAME_LENGTH:
        raise ItemNameValidationError(
            f"Item name must be at least {MIN_ITEM_NAME_LENGTH} character(s), got {len(item_name)}"
        )

    if len(item_name) > MAX_ITEM_NAME_LENGTH:
        raise ItemNameValidationError(
            f"Item name cannot exceed {MAX_ITEM_NAME_LENGTH} characters, got {len(item_name)}"
        )

    if not _ITEM_NAME_REGEX.match(item_name):
        raise ItemNameValidationError(
            f"Item name '{item_name}' contains invalid characters. "
            f"Only alphanumeric, spaces, and hyphens allowed"
        )

    return item_name


def validate_price(price: Any) -> Decimal:
    """Validate price is a Decimal between MIN_PRICE and MAX_PRICE with at most 2 decimal places."""
    validated_price: Decimal
    if not isinstance(price, Decimal):
        try:
            validated_price = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise PriceValidationError(
                f"Price must be a valid Decimal, got {type(price).__name__}: {e}"
            ) from None
    else:
        validated_price = price

    if validated_price < MIN_PRICE:
        raise PriceValidationError(f"Price cannot be negative, got {validated_price}")

    if validated_price > MAX_PRICE:
        raise PriceValidationError(f"Price cannot exceed {MAX_PRICE}, got {validated_price}")

    decimal_tuple = validated_price.as_tuple()
    if isinstance(decimal_tuple.exponent, int) and decimal_tuple.exponent < -PRICE_DECIMAL_PLACES:
        raise PriceValidationError(
            f"Price cannot have more than {PRICE_DECIMAL_PLACES} decimal places, got {validated_price}"
        )

    return validated_price


def validate_uuid4(uuid_value: Any) -> uuid.UUID:
    """Validate value is a version 4 UUID."""
    if isinstance(uuid_value, uuid.UUID):
        uuid_obj = uuid_value
    elif isinstance(uuid_value, str):
        if _contains_null_bytes(uuid_value):
            raise UUIDValidationError("UUID contains null bytes")

        try:
            uuid_obj = uuid.UUID(uuid_value)
        except ValueError as e:
            raise UUIDValidationError(f"Invalid UUID format: {e}") from None
    else:
        raise UUIDValidationError(f"UUID must be a UUID or string, got {type(uuid_value).__name__}")

    if uuid_obj.version != 4:
        raise UUIDValidationError(f"UUID must be version 4, got version {uuid_obj.version}")

    return uuid_obj
