"""Security-focused tests for attack prevention.

This module tests all security guarantees including immutability,
defensive copying, injection prevention, DoS prevention, and type confusion.
"""

import uuid
from decimal import Decimal

import pytest

from shopping_cart import Catalog, ShoppingCart
from shopping_cart.exceptions import (
    CustomerIDValidationError,
    ImmutabilityViolationError,
    ItemNameValidationError,
    ItemNotInCatalogError,
    PriceValidationError,
    QuantityValidationError,
)


class TestImmutabilityGuarantees:
    """Test that immutability guarantees cannot be violated."""

    def test_cannot_modify_cart_id_via_private_field(self):
        """Direct modification of _cart_id should fail."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ImmutabilityViolationError):
            cart._cart_id = uuid.uuid4()

    def test_cannot_modify_customer_id_via_private_field(self):
        """Direct modification of _customer_id should fail."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ImmutabilityViolationError):
            cart._customer_id = "XYZ99999ZZ-Q"

    def test_cannot_modify_cart_id_via_property(self):
        """Setting cart_id property should fail."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)
        original_id = cart.cart_id

        with pytest.raises(AttributeError):
            cart.cart_id = uuid.uuid4()

        assert cart.cart_id == original_id

    def test_cannot_modify_customer_id_via_property(self):
        """Setting customer_id property should fail."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(AttributeError):
            cart.customer_id = "XYZ99999ZZ-Q"

        assert cart.customer_id == "ABC12345XY-A"

    def test_catalog_items_are_immutable(self):
        """Catalog items should be immutable."""
        from shopping_cart.catalog import CatalogItem

        item = CatalogItem(name="Widget", price=Decimal("10.99"))

        with pytest.raises(AttributeError):
            item.price = Decimal("999.99")


class TestDefensiveCopying:
    """Test that defensive copying prevents indirect modification."""

    def test_modifying_get_items_does_not_affect_cart(self):
        """Modifying the dict returned by get_items should not affect cart."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)
        cart.add_item("Widget", 2)

        # Get items and modify
        items = cart.get_items()
        items["Widget"] = 999999
        items["Hacked Item"] = 1

        # Cart should be unchanged
        actual_items = cart.get_items()
        assert actual_items["Widget"] == 2
        assert "Hacked Item" not in actual_items
        assert cart.get_total() == Decimal("21.98")

    def test_modifying_catalog_get_all_items_does_not_affect_catalog(self):
        """Modifying dict from catalog.get_all_items should not affect catalog."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        # Get items and modify
        items = catalog.get_all_items()
        items["Widget"] = Decimal("0.01")
        items["Hacked"] = Decimal("0.01")

        # Catalog should be unchanged
        assert catalog.get_price("Widget") == Decimal("10.99")
        assert catalog.has_item("Hacked") is False

    def test_multiple_get_items_calls_return_independent_copies(self):
        """Multiple calls to get_items should return independent copies."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)
        cart.add_item("Widget", 2)

        items1 = cart.get_items()
        items2 = cart.get_items()

        # Modify first copy
        items1["Widget"] = 999
        items1["Hacked"] = 1

        # Second copy should be unchanged
        assert items2["Widget"] == 2
        assert "Hacked" not in items2


class TestSQLInjectionPrevention:
    """Test prevention of SQL injection attacks."""

    def test_sql_injection_in_customer_id(self):
        """SQL injection in customer_id should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        malicious_ids = [
            "ABC12345XY-A'; DROP TABLE customers--",
            "' OR '1'='1",
            "ABC12345XY-A' UNION SELECT * FROM users--",
            'ABC12345XY-A"; DROP TABLE carts--',
        ]

        for malicious_id in malicious_ids:
            with pytest.raises(CustomerIDValidationError):
                ShoppingCart(malicious_id, catalog)

    def test_sql_injection_in_item_name(self):
        """SQL injection in item names should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        malicious_names = [
            "Widget'; DROP TABLE items--",
            "'; DELETE FROM carts WHERE '1'='1",
            "Widget' UNION SELECT * FROM users--",
        ]

        for malicious_name in malicious_names:
            with pytest.raises(ItemNameValidationError):
                cart.add_item(malicious_name, 1)


class TestPathTraversalPrevention:
    """Test prevention of path traversal attacks."""

    def test_path_traversal_in_item_name(self):
        """Path traversal attempts in item names should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        malicious_names = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "../../../secret",
            "..\\..\\config",
        ]

        for malicious_name in malicious_names:
            with pytest.raises(ItemNameValidationError):
                cart.add_item(malicious_name, 1)


class TestNullByteInjection:
    """Test prevention of null byte injection."""

    def test_null_byte_in_customer_id(self):
        """Null bytes in customer_id should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        with pytest.raises(CustomerIDValidationError, match="null bytes"):
            ShoppingCart("ABC12345XY-A\x00", catalog)

        with pytest.raises(CustomerIDValidationError, match="null bytes"):
            ShoppingCart("\x00ABC12345XY-A", catalog)

    def test_null_byte_in_item_name(self):
        """Null bytes in item names should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ItemNameValidationError, match="null bytes"):
            cart.add_item("Widget\x00", 1)

        with pytest.raises(ItemNameValidationError, match="null bytes"):
            cart.add_item("\x00Widget", 1)


class TestDoSPrevention:
    """Test prevention of Denial of Service attacks."""

    def test_huge_quantity_rejected(self):
        """Extremely large quantities should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            cart.add_item("Widget", 999999999)

        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            cart.add_item("Widget", 100000)

    def test_very_long_item_name_rejected(self):
        """Extremely long item names should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        very_long_name = "A" * 10000

        with pytest.raises(ItemNameValidationError, match="cannot exceed"):
            cart.add_item(very_long_name, 1)

    def test_overflow_protection_when_adding_quantities(self):
        """Adding quantities that would cause overflow should be prevented."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Add item near max quantity
        cart.add_item("Widget", 9999)

        # Trying to add more should fail
        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            cart.add_item("Widget", 5)

    def test_huge_price_rejected(self):
        """Extremely large prices should be rejected."""
        with pytest.raises(PriceValidationError, match="cannot exceed"):
            Catalog({"Widget": Decimal("10000000.00")})


class TestTypeConfusion:
    """Test prevention of type confusion attacks."""

    def test_customer_id_must_be_string(self):
        """Customer ID must be a string, not other types."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            ShoppingCart(123, catalog)

        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            ShoppingCart(["ABC12345XY-A"], catalog)

        with pytest.raises(CustomerIDValidationError, match="must be a string"):
            ShoppingCart(None, catalog)

    def test_quantity_must_be_int(self):
        """Quantity must be an integer, not other types."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(QuantityValidationError, match="must be an integer"):
            cart.add_item("Widget", "5")

        with pytest.raises(QuantityValidationError, match="must be an integer"):
            cart.add_item("Widget", 5.5)

        with pytest.raises(QuantityValidationError, match="must be an integer"):
            cart.add_item("Widget", True)  # Boolean is rejected

    def test_item_name_must_be_string(self):
        """Item name must be a string, not other types."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ItemNameValidationError, match="must be a string"):
            cart.add_item(123, 1)

        with pytest.raises(ItemNameValidationError, match="must be a string"):
            cart.add_item(["Widget"], 1)

    def test_catalog_must_be_catalog_instance(self):
        """Catalog parameter must be a Catalog instance."""
        with pytest.raises(TypeError, match="must be a Catalog"):
            ShoppingCart("ABC12345XY-A", {"Widget": Decimal("10.99")})

        with pytest.raises(TypeError, match="must be a Catalog"):
            ShoppingCart("ABC12345XY-A", None)


class TestDecimalPrecisionAttacks:
    """Test prevention of decimal precision-based attacks."""

    def test_price_with_too_many_decimals_rejected(self):
        """Prices with too many decimal places should be rejected."""
        with pytest.raises(PriceValidationError, match="decimal places"):
            Catalog({"Widget": Decimal("10.999")})

        with pytest.raises(PriceValidationError, match="decimal places"):
            Catalog({"Widget": Decimal("10.12345")})

    def test_decimal_precision_maintained_in_total(self):
        """Total calculation should maintain proper decimal precision."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        cart.add_item("Widget", 3)
        total = cart.get_total()

        # Should be exactly 32.97, not floating point approximation
        assert total == Decimal("32.97")
        assert isinstance(total, Decimal)

    def test_negative_price_rejected(self):
        """Negative prices should be rejected."""
        with pytest.raises(PriceValidationError, match="cannot be negative"):
            Catalog({"Widget": Decimal("-10.99")})


class TestUnicodeAndControlCharacters:
    """Test handling of unicode and control characters."""

    def test_control_characters_in_customer_id(self):
        """Control characters in customer_id should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        with pytest.raises(CustomerIDValidationError, match="control characters"):
            ShoppingCart("ABC12345XY-A\x01", catalog)

        with pytest.raises(CustomerIDValidationError, match="control characters"):
            ShoppingCart("ABC\r\n12345XY-A", catalog)

    def test_control_characters_in_item_name(self):
        """Control characters in item names should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ItemNameValidationError, match="control characters"):
            cart.add_item("Widget\x01", 1)

        with pytest.raises(ItemNameValidationError, match="control characters"):
            cart.add_item("Widget\r\n", 1)

    def test_unicode_characters_in_item_name(self):
        """Unicode characters beyond ASCII should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ItemNameValidationError):
            cart.add_item("Wìdgét", 1)

        with pytest.raises(ItemNameValidationError):
            cart.add_item("Widget™", 1)


class TestCatalogEnforcement:
    """Test that catalog enforcement prevents fake items."""

    def test_cannot_add_item_not_in_catalog(self):
        """Items not in catalog should be rejected."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        with pytest.raises(ItemNotInCatalogError):
            cart.add_item("Nonexistent", 1)

        with pytest.raises(ItemNotInCatalogError):
            cart.add_item("Hacked Item", 1)

    def test_catalog_validation_on_all_operations(self):
        """All cart operations should respect catalog."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Add valid item
        cart.add_item("Widget", 1)

        # Cannot update non-catalog item (even though update doesn't check catalog,
        # the item must be added first which does check)
        with pytest.raises(ItemNotInCatalogError):
            cart.add_item("Fake", 1)


class TestIntegrityMaintenance:
    """Test that data integrity is maintained under all conditions."""

    def test_cart_state_consistent_after_failed_operation(self):
        """Cart state should remain consistent after failed operations."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        cart.add_item("Widget", 5)
        original_total = cart.get_total()

        # Try invalid operation
        with pytest.raises(ItemNotInCatalogError):
            cart.add_item("Fake", 1)

        # Cart should be unchanged
        assert cart.get_total() == original_total
        assert cart.get_items() == {"Widget": 5}

    def test_no_silent_failures(self):
        """Invalid operations should raise exceptions, never fail silently."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # All these should raise specific exceptions
        with pytest.raises(QuantityValidationError):
            cart.add_item("Widget", 0)

        with pytest.raises(ItemNotInCatalogError):
            cart.add_item("Fake", 1)

        with pytest.raises(ItemNameValidationError):
            cart.add_item("Invalid@Name", 1)

        # Cart should still be empty
        assert cart.get_items() == {}
        assert cart.get_total() == Decimal("0.00")
