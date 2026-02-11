# Security Design Documentation

This document describes the security design principles and threat model for the Shopping Cart Library.

## Threat Model

### Assets
- Cart data integrity (items, quantities, totals)
- Customer identity (customer_id)
- Catalog integrity (prices, available items)
- Cart identity (cart_id uniqueness)

### Threats
1. **Injection Attacks**: SQL injection, path traversal, null byte injection
2. **DoS Attacks**: Resource exhaustion via large inputs
3. **Type Confusion**: Bypassing validation via type tricks
4. **State Tampering**: Modifying immutable IDs or internal state
5. **Precision Attacks**: Exploiting floating-point arithmetic
6. **Data Corruption**: Invalid data causing integrity violations

## Security Guarantees

### 1. Immutability

**Implementation:**
- `__setattr__` override blocks modification of `_cart_id` and `_customer_id`
- Properties provide read-only access
- Frozen dataclasses for CatalogItem
- Attempts raise `ImmutabilityViolationError`

**Protection:** Prevents ID tampering after creation

### 2. Defensive Copying

**Implementation:**
- `get_items()` returns `deepcopy()` of internal dict
- `get_all_items()` returns `deepcopy()` of catalog
- No references to internal mutable state escape

**Protection:** Prevents indirect state modification

### 3. Input Validation

**Implementation:**
- Pre-compiled regex (prevents ReDoS)
- Type checking with isinstance
- Bounds checking on all numeric values
- Character whitelisting
- Null byte detection
- Control character rejection

**Protection:** Prevents injection, DoS, and type confusion

### 4. Catalog Enforcement

**Implementation:**
- All add operations check `catalog.has_item()`
- Catalog is immutable after creation
- Prices cannot be modified

**Protection:** Prevents fake items and price manipulation

### 5. Decimal Precision

**Implementation:**
- All monetary values use `Decimal` type
- Validation enforces 2 decimal places
- No floating-point arithmetic

**Protection:** Prevents precision-based attacks

### 6. Fail-Fast Design

**Implementation:**
- Specific exceptions for all error conditions
- No silent failures or default values
- Operations are atomic (no partial updates)

**Protection:** Maintains data integrity

## Validation Rules

### Customer ID
- Pattern: `^[A-Z]{3}\d{5}[A-Z]{2}-(A|Q)$`
- No null bytes or control characters
- Type must be string

### Item Names
- Length: 1-100 characters
- Pattern: `^[a-zA-Z0-9\s\-]+$`
- No null bytes or control characters
- Type must be string

### Quantities
- Range: 1-10,000
- Type must be int (not bool)
- Overflow protection on addition

### Prices
- Range: 0.00-999,999.99
- Type: Decimal
- Maximum 2 decimal places
- No negative values

## Attack Prevention

### SQL Injection
- Character whitelisting blocks SQL metacharacters
- No special characters allowed in item names or customer IDs

### Path Traversal
- Alphanumeric + space + hyphen only in item names
- `.` and `/` characters blocked

### Null Byte Injection
- Explicit check for `\x00` in all string inputs
- Rejected before other validation

### DoS via Large Inputs
- Maximum quantity: 10,000
- Maximum item name length: 100
- Maximum price: 999,999.99
- Prevents resource exhaustion

### Type Confusion
- Strict type checking with isinstance
- Boolean explicitly rejected (isinstance(True, int) is True in Python)
- Invalid types raise specific exceptions

### Decimal Precision Attacks
- Validation enforces exactly 2 decimal places
- Attempts to use more precision rejected
- All arithmetic uses Decimal type

### Control Characters
- ASCII control characters (0x00-0x1F) rejected
- Exceptions for \n and \t (not used in validation contexts)

## Zero Trust Principles

1. **Validate Everything**: All inputs validated, no assumptions
2. **Trust Nothing**: Even internal operations validated
3. **Fail Securely**: Invalid data raises exceptions
4. **Defense in Depth**: Multiple validation layers
5. **Least Privilege**: Read-only catalog, immutable IDs
6. **Complete Mediation**: All operations go through validators

## Testing Strategy

- **test_validators.py**: Unit tests for all validation logic
- **test_security.py**: Attack scenario testing
- **test_integration.py**: End-to-end workflows
- **Coverage target**: 90%+

## Dependencies

**Runtime:** None (stdlib only)

This eliminates supply chain attack vectors.

**Development:**
- pytest (testing)
- mypy (type checking)
- ruff (security linting)

All dev dependencies are well-established, widely-used tools.

## Known Limitations

1. **In-Memory Only**: No persistence (out of scope)
2. **Single-Threaded**: No concurrency protection (out of scope)
3. **No Authentication**: Customer ID validation only (out of scope)
4. **No Encryption**: Data stored in plain text (out of scope)

These limitations are acceptable for a library-level component. Applications using this library must implement their own persistence, concurrency control, authentication, and encryption as needed.
