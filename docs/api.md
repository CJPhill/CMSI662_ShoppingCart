# API Documentation

Complete API reference for the Shopping Cart Library.

See README.md for a quick start guide. This document provides comprehensive details on all classes, methods, and exceptions.

## Catalog Class

**Module:** `shopping_cart.catalog`

### Constructor

`Catalog(items: Dict[ItemName, Price])`

Creates an immutable product catalog.

**Parameters:**
- `items`: Dictionary mapping item names (str) to prices (Decimal)

**Returns:** Catalog instance

**Raises:**
- `ItemNameValidationError`: Invalid item name
- `PriceValidationError`: Invalid price

### Methods

- `has_item(item_name: str) -> bool`: Check if item exists
- `get_price(item_name: str) -> Optional[Decimal]`: Get item price (None if not found)
- `get_all_items() -> Dict[str, Decimal]`: Get all items (defensive copy)

## ShoppingCart Class

**Module:** `shopping_cart.cart`

### Constructor

`ShoppingCart(customer_id: str, catalog: Catalog)`

Creates a shopping cart with unique UUID4 cart_id.

**Parameters:**
- `customer_id`: Format XXX#####XX-[A|Q]
- `catalog`: Catalog instance for validation

**Properties (read-only):**
- `cart_id`: UUID4 identifier
- `customer_id`: Customer identifier string

### Methods

- `add_item(item_name, quantity)`: Add item or increase quantity
- `update_item_quantity(item_name, quantity)`: Set item quantity
- `remove_item(item_name)`: Remove item from cart
- `get_items() -> Dict[str, int]`: Get items (defensive copy)
- `get_total() -> Decimal`: Calculate total cost

## Exceptions

All exceptions inherit from `ShoppingCartError`.

- `ValidationError`: Base for validation errors
- `CustomerIDValidationError`: Invalid customer ID format
- `QuantityValidationError`: Invalid quantity
- `ItemNameValidationError`: Invalid item name
- `PriceValidationError`: Invalid price
- `UUIDValidationError`: Invalid UUID
- `ImmutabilityViolationError`: Attempted modification of immutable field
- `ItemNotInCatalogError`: Item not in catalog
- `ItemNotInCartError`: Item not in cart

See README.md for complete examples and usage patterns.
