# Shopping Cart Library

A secure shopping cart module for **CMSI 662 Assignment 1, Part 5**.

## Assignment Requirements

| Requirement | Implementation |
|-------------|----------------|
| Cart has its own ID | UUID4 generated on creation (`cart.cart_id`) |
| Cart holds customer ID | Validated on creation (`cart.customer_id`) |
| Cart holds items with quantities | Dict stored internally, accessed via `get_items()` |
| Query id, customer id, items | Read-only properties and `get_items()` method |
| Immutability / defensive copying | `get_items()` returns deep copy; IDs blocked from modification via `__setattr__` |
| Add, update, remove items | `add_item()`, `update_item_quantity()`, `remove_item()` |
| ID and customer ID immutable | `__setattr__` raises `ImmutabilityViolationError` on attempts |
| Get total cost | `get_total()` returns `Decimal` |
| Cart ID as UUID4 | Generated via `uuid.uuid4()` |
| Customer ID format: 3 letters, 5 numbers, 2 letters, dash, A or Q | Regex: `^[A-Z]{3}\d{5}[A-Z]{2}-(A\|Q)$` |
| No negative quantities | Validated; minimum quantity is 1 |
| Upper bounds on quantities | Maximum quantity is 10,000 |
| Items must be in catalog | `add_item()` checks `catalog.has_item()` |
| Catalog is read-only | `Catalog` class provides only read methods |
| Item names length-bounded and character-restricted | 1-100 chars, alphanumeric + space + hyphen only |
| Fail-fast with exceptions | Custom exceptions for all error conditions |

## Quick Start

```python
from decimal import Decimal
from shopping_cart import Catalog, ShoppingCart

catalog = Catalog({"Widget": Decimal("10.99"), "Gadget": Decimal("25.50")})
cart = ShoppingCart("ABC12345XY-A", catalog)

cart.add_item("Widget", 2)
cart.add_item("Gadget", 1)
print(cart.get_total())  # Decimal('47.48')
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Project Structure

```
src/shopping_cart/   # Library code
  cart.py            # ShoppingCart class
  catalog.py         # Catalog class
  validators.py      # Input validation
  exceptions.py      # Custom exceptions
tests/               # Unit and integration tests
```