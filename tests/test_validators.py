"""Comprehensive tests for validation layer."""

import uuid
from decimal import Decimal

import pytest

from shopping_cart.exceptions import (
    CustomerIDValidationError,
    ItemNameValidationError,
    PriceValidationError,
    QuantityValidationError,
    UUIDValidationError,
)
from shopping_cart.types import (
    MAX_ITEM_NAME_LENGTH,
    MAX_PRICE,
    MAX_QUANTITY,
    MIN_PRICE,
    MIN_QUANTITY,
)
from shopping_cart.validators import (
    validate_customer_id,
    validate_item_name,
    validate_price,
    validate_quantity,
    validate_uuid4,
)


class TestCustomerIDValidation:
    """Test customer ID validation."""

    def test_valid_customer_ids(self):
        """Valid customer IDs should pass validation."""
        valid_ids = [
            "ABC12345XY-A",
            "XYZ99999ZZ-Q",
            "AAA00000AA-A",
            "ZZZ99999ZZ-Q",
        ]
        for customer_id in valid_ids:
            assert validate_customer_id(customer_id) == customer_id

    def test_invalid_type(self):
        """Non-string types should raise error."""
        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            validate_customer_id(12345)

        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            validate_customer_id(None)

        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            validate_customer_id(["ABC12345XY-A"])

    def test_invalid_formats(self):
        """Invalid formats should raise error."""
        invalid_ids = [
            "abc12345XY-A",  # Lowercase first part
            "ABC12345xy-A",  # Lowercase second part
            "AB12345XY-A",  # Too few letters (first part)
            "ABC1234XY-A",  # Too few digits
            "ABC123456XY-A",  # Too many digits
            "ABC12345X-A",  # Too few letters (second part)
            "ABC12345XY-B",  # Invalid suffix (not A or Q)
            "ABC12345XY-a",  # Lowercase suffix
            "ABC12345XYA",  # Missing hyphen
            "ABC-12345-XY-A",  # Extra hyphens
            "",  # Empty string
            "ABC12345XY-AQ",  # Too long suffix
        ]
        for customer_id in invalid_ids:
            with pytest.raises(CustomerIDValidationError):
                validate_customer_id(customer_id)

    def test_null_byte_injection(self):
        """Null bytes should be rejected."""
        with pytest.raises(CustomerIDValidationError, match="null bytes"):
            validate_customer_id("ABC12345XY-A\x00")

        with pytest.raises(CustomerIDValidationError, match="null bytes"):
            validate_customer_id("\x00ABC12345XY-A")

    def test_control_characters(self):
        """Control characters should be rejected."""
        with pytest.raises(CustomerIDValidationError, match="control characters"):
            validate_customer_id("ABC12345XY-A\x01")

        with pytest.raises(CustomerIDValidationError, match="control characters"):
            validate_customer_id("ABC\x1f12345XY-A")

    def test_sql_injection_attempt(self):
        """SQL injection attempts should be rejected."""
        with pytest.raises(CustomerIDValidationError):
            validate_customer_id("ABC12345XY-A'; DROP TABLE users--")

        with pytest.raises(CustomerIDValidationError):
            validate_customer_id("' OR '1'='1")


class TestQuantityValidation:
    """Test quantity validation."""

    def test_valid_quantities(self):
        """Valid quantities should pass validation."""
        assert validate_quantity(1) == 1
        assert validate_quantity(10) == 10
        assert validate_quantity(100) == 100
        assert validate_quantity(MAX_QUANTITY) == MAX_QUANTITY

    def test_boundary_values(self):
        """Boundary values should be handled correctly."""
        # Min boundary
        assert validate_quantity(MIN_QUANTITY) == MIN_QUANTITY

        # Max boundary
        assert validate_quantity(MAX_QUANTITY) == MAX_QUANTITY

        # Just below min
        with pytest.raises(QuantityValidationError, match="at least"):
            validate_quantity(MIN_QUANTITY - 1)

        # Just above max
        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            validate_quantity(MAX_QUANTITY + 1)

    def test_invalid_type(self):
        """Non-integer types should raise error."""
        with pytest.raises(QuantityValidationError, match="must be an integer"):
            validate_quantity("5")

        with pytest.raises(QuantityValidationError, match="must be an integer"):
            validate_quantity(5.5)

        with pytest.raises(QuantityValidationError, match="must be an integer"):
            validate_quantity(None)

        # Boolean should be rejected (isinstance(True, int) is True in Python)
        with pytest.raises(QuantityValidationError, match="must be an integer"):
            validate_quantity(True)

    def test_negative_quantity(self):
        """Negative quantities should be rejected."""
        with pytest.raises(QuantityValidationError, match="at least"):
            validate_quantity(-1)

        with pytest.raises(QuantityValidationError, match="at least"):
            validate_quantity(-100)

    def test_zero_quantity(self):
        """Zero quantity should be rejected."""
        with pytest.raises(QuantityValidationError, match="at least"):
            validate_quantity(0)

    def test_dos_attempt_huge_number(self):
        """Extremely large numbers should be rejected."""
        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            validate_quantity(999999999)

        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            validate_quantity(MAX_QUANTITY + 1000)


class TestItemNameValidation:
    """Test item name validation."""

    def test_valid_item_names(self):
        """Valid item names should pass validation."""
        valid_names = [
            "Widget",
            "Super Widget",
            "Widget-2000",
            "A",
            "a" * MAX_ITEM_NAME_LENGTH,
            "Multi-Word Product Name",
            "Product123",
        ]
        for name in valid_names:
            assert validate_item_name(name) == name

    def test_invalid_type(self):
        """Non-string types should raise error."""
        with pytest.raises(ItemNameValidationError, match="must be a string"):
            validate_item_name(123)

        with pytest.raises(ItemNameValidationError, match="must be a string"):
            validate_item_name(None)

    def test_length_constraints(self):
        """Length constraints should be enforced."""
        # Empty string
        with pytest.raises(ItemNameValidationError, match="at least"):
            validate_item_name("")

        # Too long
        with pytest.raises(ItemNameValidationError, match="cannot exceed"):
            validate_item_name("a" * (MAX_ITEM_NAME_LENGTH + 1))

        # Exactly max length (should pass)
        long_name = "a" * MAX_ITEM_NAME_LENGTH
        assert validate_item_name(long_name) == long_name

    def test_invalid_characters(self):
        """Invalid characters should be rejected."""
        invalid_names = [
            "Widget!",
            "Widget@Home",
            "Widget#1",
            "Widget$",
            "Widget%Off",
            "Widget&Co",
            "Widget*",
            "Widget(Special)",
            "Widget;",
            "Widget:",
            "Widget/",
            "Widget\\",
            "Widget|",
            "Widget<>",
            "Widget?",
            "Widget=",
            "Widget+",
        ]
        for name in invalid_names:
            with pytest.raises(ItemNameValidationError, match="invalid characters"):
                validate_item_name(name)

    def test_null_byte_injection(self):
        """Null bytes should be rejected."""
        with pytest.raises(ItemNameValidationError, match="null bytes"):
            validate_item_name("Widget\x00")

    def test_control_characters(self):
        """Control characters should be rejected."""
        with pytest.raises(ItemNameValidationError, match="control characters"):
            validate_item_name("Widget\x01")

        with pytest.raises(ItemNameValidationError, match="control characters"):
            validate_item_name("Widget\r\n")

    def test_path_traversal_attempt(self):
        """Path traversal attempts should be rejected."""
        with pytest.raises(ItemNameValidationError):
            validate_item_name("../../etc/passwd")

        with pytest.raises(ItemNameValidationError):
            validate_item_name("..\\..\\windows\\system32")

    def test_sql_injection_attempt(self):
        """SQL injection attempts should be rejected."""
        with pytest.raises(ItemNameValidationError):
            validate_item_name("Widget'; DROP TABLE items--")

    def test_dos_attempt_very_long_string(self):
        """Very long strings should be rejected."""
        with pytest.raises(ItemNameValidationError, match="cannot exceed"):
            validate_item_name("a" * 10000)

    def test_unicode_edge_cases(self):
        """Unicode characters should be rejected (alphanumeric only)."""
        with pytest.raises(ItemNameValidationError):
            validate_item_name("Wìdgét")  # Accented characters

        with pytest.raises(ItemNameValidationError):
            validate_item_name("Widget™")  # Trademark symbol

        with pytest.raises(ItemNameValidationError):
            validate_item_name("Widget™️")  # Emoji


class TestPriceValidation:
    """Test price validation."""

    def test_valid_prices(self):
        """Valid prices should pass validation."""
        valid_prices = [
            Decimal("0.00"),
            Decimal("0.01"),
            Decimal("10.99"),
            Decimal("100.00"),
            Decimal("999999.99"),
        ]
        for price in valid_prices:
            assert validate_price(price) == price

    def test_conversion_from_string(self):
        """String prices should be converted to Decimal."""
        assert validate_price("10.99") == Decimal("10.99")
        assert validate_price("0.00") == Decimal("0.00")

    def test_invalid_type(self):
        """Invalid types should raise error."""
        with pytest.raises(PriceValidationError, match="valid Decimal"):
            validate_price(None)

        with pytest.raises(PriceValidationError, match="valid Decimal"):
            validate_price("invalid")

        with pytest.raises(PriceValidationError, match="valid Decimal"):
            validate_price([10.99])

    def test_negative_price(self):
        """Negative prices should be rejected."""
        with pytest.raises(PriceValidationError, match="cannot be negative"):
            validate_price(Decimal("-0.01"))

        with pytest.raises(PriceValidationError, match="cannot be negative"):
            validate_price(Decimal("-10.99"))

    def test_price_exceeds_maximum(self):
        """Prices exceeding maximum should be rejected."""
        with pytest.raises(PriceValidationError, match="cannot exceed"):
            validate_price(Decimal("1000000.00"))

        with pytest.raises(PriceValidationError, match="cannot exceed"):
            validate_price(MAX_PRICE + Decimal("0.01"))

    def test_boundary_values(self):
        """Boundary values should be handled correctly."""
        # Min boundary
        assert validate_price(MIN_PRICE) == MIN_PRICE

        # Max boundary
        assert validate_price(MAX_PRICE) == MAX_PRICE

    def test_decimal_precision(self):
        """Decimal precision should be enforced."""
        # Valid precision (2 decimal places)
        assert validate_price(Decimal("10.99")) == Decimal("10.99")

        # Too many decimal places
        with pytest.raises(PriceValidationError, match="decimal places"):
            validate_price(Decimal("10.999"))

        with pytest.raises(PriceValidationError, match="decimal places"):
            validate_price(Decimal("10.1234"))

        # Integer prices are OK (0 decimal places)
        assert validate_price(Decimal("10")) == Decimal("10")

        # One decimal place is OK
        assert validate_price(Decimal("10.5")) == Decimal("10.5")

    def test_floating_point_conversion(self):
        """Float prices should be converted correctly."""
        # This tests that we use Decimal for precision
        assert validate_price(10.99) == Decimal("10.99")

    def test_precision_attack(self):
        """Precision-based attacks should be prevented."""
        with pytest.raises(PriceValidationError, match="decimal places"):
            validate_price(Decimal("0.001"))


class TestUUIDValidation:
    """Test UUID validation."""

    def test_valid_uuid4(self):
        """Valid UUID4 should pass validation."""
        valid_uuid = uuid.uuid4()
        assert validate_uuid4(valid_uuid) == valid_uuid

    def test_valid_uuid4_string(self):
        """Valid UUID4 string should pass validation."""
        valid_uuid = uuid.uuid4()
        uuid_str = str(valid_uuid)
        assert validate_uuid4(uuid_str) == valid_uuid

    def test_invalid_type(self):
        """Invalid types should raise error."""
        with pytest.raises(UUIDValidationError, match="must be a UUID or string"):
            validate_uuid4(123)

        with pytest.raises(UUIDValidationError, match="must be a UUID or string"):
            validate_uuid4(None)

    def test_invalid_uuid_string(self):
        """Invalid UUID strings should raise error."""
        with pytest.raises(UUIDValidationError, match="Invalid UUID format"):
            validate_uuid4("not-a-uuid")

        with pytest.raises(UUIDValidationError, match="Invalid UUID format"):
            validate_uuid4("12345")

    def test_wrong_uuid_version(self):
        """Non-version-4 UUIDs should be rejected."""
        # UUID version 1
        uuid1 = uuid.uuid1()
        with pytest.raises(UUIDValidationError, match="must be version 4"):
            validate_uuid4(uuid1)

        # UUID version 5
        uuid5 = uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")
        with pytest.raises(UUIDValidationError, match="must be version 4"):
            validate_uuid4(uuid5)

    def test_null_byte_in_uuid_string(self):
        """Null bytes in UUID string should be rejected."""
        valid_uuid = str(uuid.uuid4())
        with pytest.raises(UUIDValidationError, match="null bytes"):
            validate_uuid4(valid_uuid + "\x00")
