"""Type definitions and constants for the shopping cart library."""

from decimal import Decimal

ItemName = str
Quantity = int
Price = Decimal
CartItems = dict[ItemName, Quantity]

MIN_QUANTITY = 1
MAX_QUANTITY = 10000
MIN_ITEM_NAME_LENGTH = 1
MAX_ITEM_NAME_LENGTH = 100
MIN_PRICE = Decimal("0.00")
MAX_PRICE = Decimal("999999.99")
PRICE_DECIMAL_PLACES = 2

CUSTOMER_ID_PATTERN = r"^[A-Z]{3}\d{5}[A-Z]{2}-(A|Q)$"
ITEM_NAME_PATTERN = r"^[a-zA-Z0-9\s\-]+$"
