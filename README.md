# Shopping Cart Library

A secure, production-ready shopping cart library implemented in Python with comprehensive security features including immutability guarantees, defensive programming, and extensive input validation.

Developed for CMSI662 (Software Security) to demonstrate security-first development practices.

## Features

- **Immutable IDs**: Cart ID and Customer ID cannot be modified after creation
- **Defensive Copying**: All query methods return defensive copies to prevent indirect modification
- **Comprehensive Validation**: All inputs validated against injection attacks, DoS attempts, and type confusion
- **Catalog Enforcement**: Only items from the read-only catalog can be added to carts
- **Decimal Precision**: Monetary calculations use Decimal type for accuracy
- **Zero Runtime Dependencies**: Uses only Python standard library

## Security Guarantees

- **Immutability**: Cart and customer IDs are immutable after creation
- **No Injection Attacks**: Protection against SQL injection, path traversal, null byte injection
- **DoS Prevention**: Bounds checking on quantities, string lengths, and prices
- **Type Safety**: Strict type checking with specific validation errors
- **Data Integrity**: Fail-fast design with no silent failures
- **Defensive Copying**: Internal state cannot be modified through returned references

## Installation

```bash
cd CMSI662_ShoppingCart

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install the package
pip install -e .
```

## Quick Start

```python
from decimal import Decimal
from shopping_cart import Catalog, ShoppingCart

# Create a product catalog
catalog = Catalog({
    "Widget": Decimal("10.99"),
    "Gadget": Decimal("25.50"),
    "Doohickey": Decimal("5.00"),
})

# Create a shopping cart (customer ID format: XXX#####XX-[A|Q])
cart = ShoppingCart("ABC12345XY-A", catalog)

# Add items to cart
cart.add_item("Widget", 2)
cart.add_item("Gadget", 1)

# Get cart total
total = cart.get_total()  # Decimal('47.48')

# Update item quantity
cart.update_item_quantity("Widget", 5)

# Remove item
cart.remove_item("Gadget")

# Get all items (returns defensive copy)
items = cart.get_items()  # {"Widget": 5}

# Cart properties are immutable
cart_id = cart.cart_id  # UUID4
customer_id = cart.customer_id  # "ABC12345XY-A"
```

## API Overview

### Catalog

```python
catalog = Catalog(items: Dict[str, Decimal])
catalog.has_item(item_name: str) -> bool
catalog.get_price(item_name: str) -> Optional[Decimal]
catalog.get_all_items() -> Dict[str, Decimal]  # Returns defensive copy
```

### ShoppingCart

```python
cart = ShoppingCart(customer_id: str, catalog: Catalog)

# Properties (read-only)
cart.cart_id  # UUID4
cart.customer_id  # str

# Methods
cart.add_item(item_name: str, quantity: int) -> None
cart.update_item_quantity(item_name: str, quantity: int) -> None
cart.remove_item(item_name: str) -> None
cart.get_items() -> Dict[str, int]  # Returns defensive copy
cart.get_total() -> Decimal
```

## Input Validation Rules

### Customer ID
- Format: `XXX#####XX-[A|Q]`
- 3 uppercase letters + 5 digits + 2 uppercase letters + hyphen + A or Q
- Example: `ABC12345XY-A`

### Item Names
- Length: 1-100 characters
- Characters: Alphanumeric, spaces, and hyphens only
- No special characters, control characters, or null bytes

### Quantities
- Range: 1-10,000
- Must be positive integer
- Overflow protection when adding to existing quantities

### Prices
- Type: Decimal
- Range: 0.00-999,999.99
- Maximum 2 decimal places
- No negative values

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/shopping_cart --cov-report=term-missing

# Run specific test suites
pytest tests/test_validators.py -v
pytest tests/test_security.py -v
pytest tests/test_integration.py -v

# Type checking
mypy src/shopping_cart --strict

# Linting
ruff check src/shopping_cart

# Formatting
black src/shopping_cart
```

## Project Structure

```
CMSI662_ShoppingCart/
├── src/
│   └── shopping_cart/
│       ├── __init__.py          # Public API exports
│       ├── types.py             # Constants and type aliases
│       ├── exceptions.py        # Custom exception hierarchy
│       ├── validators.py        # Input validation layer
│       ├── catalog.py           # Read-only product catalog
│       └── cart.py              # ShoppingCart class
├── tests/
│   ├── test_validators.py      # Validation tests
│   ├── test_catalog.py         # Catalog tests
│   ├── test_cart.py            # Cart functionality tests
│   ├── test_security.py        # Security-focused tests
│   └── test_integration.py     # Integration tests
├── docs/
│   ├── api.md                  # Detailed API documentation
│   └── security.md             # Security design documentation
├── pyproject.toml              # Project configuration
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## Security Features

### Immutability
- Cart ID (UUID4) cannot be changed after creation
- Customer ID cannot be changed after creation
- Catalog items are frozen dataclasses
- All ID modification attempts raise `ImmutabilityViolationError`

### Defensive Copying
- `get_items()` returns a deep copy of cart items
- `get_all_items()` returns a deep copy of catalog items
- Modifying returned data does not affect internal state

### Input Validation
- Pre-compiled regex patterns (prevents ReDoS attacks)
- Type checking at all boundaries
- Bounds checking on all numeric values
- Character whitelisting for strings
- Null byte and control character rejection

### Attack Prevention
- **SQL Injection**: Input validation rejects SQL metacharacters
- **Path Traversal**: Character restrictions prevent path navigation
- **DoS**: Upper bounds on quantities, string lengths, and prices
- **Type Confusion**: Strict type checking with Boolean rejection
- **Precision Attacks**: Decimal validation enforces 2 decimal places
- **Null Byte Injection**: Explicit null byte detection

## Exception Hierarchy

```
ShoppingCartError
├── ValidationError
│   ├── CustomerIDValidationError
│   ├── QuantityValidationError
│   ├── ItemNameValidationError
│   ├── PriceValidationError
│   └── UUIDValidationError
├── ImmutabilityViolationError
├── ItemNotInCatalogError
└── ItemNotInCartError
```

## License

MIT License - See LICENSE file for details

## Contributing

This is an academic project for CMSI662. For questions or issues, please contact the course instructor.

## Acknowledgments

Built with security-first principles taught in CMSI662 (Software Security) at Loyola Marymount University.