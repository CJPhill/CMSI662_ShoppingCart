"""Tests for shopping cart implementation."""

import uuid
from decimal import Decimal

import pytest

from shopping_cart import Catalog, ShoppingCart
from shopping_cart.exceptions import (
    CustomerIDValidationError,
    ImmutabilityViolationError,
    ItemNameValidationError,
    ItemNotInCartError,
    ItemNotInCatalogError,
    QuantityValidationError,
)


@pytest.fixture
def sample_catalog():
    """Create a sample catalog for testing."""
    return Catalog(
        {
            "Widget": Decimal("10.99"),
            "Gadget": Decimal("25.50"),
            "Doohickey": Decimal("5.00"),
        }
    )


@pytest.fixture
def sample_cart(sample_catalog):
    """Create a sample cart for testing."""
    return ShoppingCart("ABC12345XY-A", sample_catalog)


class TestShoppingCartCreation:
    """Test shopping cart creation."""

    def test_create_cart(self, sample_catalog):
        """Cart should be created with valid customer ID."""
        cart = ShoppingCart("ABC12345XY-A", sample_catalog)

        assert cart.customer_id == "ABC12345XY-A"
        assert isinstance(cart.cart_id, uuid.UUID)
        assert cart.cart_id.version == 4

    def test_unique_cart_ids(self, sample_catalog):
        """Each cart should have a unique ID."""
        cart1 = ShoppingCart("ABC12345XY-A", sample_catalog)
        cart2 = ShoppingCart("ABC12345XY-A", sample_catalog)

        assert cart1.cart_id != cart2.cart_id

    def test_invalid_customer_id(self, sample_catalog):
        """Invalid customer IDs should raise error."""
        with pytest.raises(CustomerIDValidationError):
            ShoppingCart("invalid", sample_catalog)

    def test_invalid_catalog_type(self):
        """Non-Catalog type should raise error."""
        with pytest.raises(TypeError, match="must be a Catalog"):
            ShoppingCart("ABC12345XY-A", {})

        with pytest.raises(TypeError, match="must be a Catalog"):
            ShoppingCart("ABC12345XY-A", None)


class TestAddItem:
    """Test adding items to cart."""

    def test_add_single_item(self, sample_cart):
        """Adding a single item should work."""
        sample_cart.add_item("Widget", 1)
        items = sample_cart.get_items()

        assert items["Widget"] == 1
        assert len(items) == 1

    def test_add_multiple_items(self, sample_cart):
        """Adding multiple different items should work."""
        sample_cart.add_item("Widget", 2)
        sample_cart.add_item("Gadget", 3)

        items = sample_cart.get_items()
        assert items["Widget"] == 2
        assert items["Gadget"] == 3
        assert len(items) == 2

    def test_add_same_item_twice(self, sample_cart):
        """Adding the same item twice should increase quantity."""
        sample_cart.add_item("Widget", 2)
        sample_cart.add_item("Widget", 3)

        items = sample_cart.get_items()
        assert items["Widget"] == 5

    def test_add_item_not_in_catalog(self, sample_cart):
        """Adding item not in catalog should raise error."""
        with pytest.raises(ItemNotInCatalogError, match="does not exist in the catalog"):
            sample_cart.add_item("Nonexistent", 1)

    def test_add_invalid_quantity(self, sample_cart):
        """Invalid quantities should raise error."""
        with pytest.raises(QuantityValidationError):
            sample_cart.add_item("Widget", 0)

        with pytest.raises(QuantityValidationError):
            sample_cart.add_item("Widget", -1)

        with pytest.raises(QuantityValidationError):
            sample_cart.add_item("Widget", 10001)

    def test_add_invalid_item_name(self, sample_cart):
        """Invalid item names should raise error."""
        with pytest.raises(ItemNameValidationError):
            sample_cart.add_item("Invalid@Name", 1)

    def test_overflow_protection(self, sample_cart):
        """Adding quantities that would exceed max should raise error."""
        sample_cart.add_item("Widget", 9000)

        with pytest.raises(QuantityValidationError, match="cannot exceed"):
            sample_cart.add_item("Widget", 2000)  # Would total 11000


class TestUpdateItemQuantity:
    """Test updating item quantities."""

    def test_update_quantity(self, sample_cart):
        """Updating quantity should replace the current quantity."""
        sample_cart.add_item("Widget", 5)
        sample_cart.update_item_quantity("Widget", 3)

        items = sample_cart.get_items()
        assert items["Widget"] == 3

    def test_update_nonexistent_item(self, sample_cart):
        """Updating item not in cart should raise error."""
        with pytest.raises(ItemNotInCartError, match="not in the cart"):
            sample_cart.update_item_quantity("Widget", 5)

    def test_update_invalid_quantity(self, sample_cart):
        """Invalid quantities should raise error."""
        sample_cart.add_item("Widget", 5)

        with pytest.raises(QuantityValidationError):
            sample_cart.update_item_quantity("Widget", 0)

        with pytest.raises(QuantityValidationError):
            sample_cart.update_item_quantity("Widget", -1)


class TestRemoveItem:
    """Test removing items from cart."""

    def test_remove_item(self, sample_cart):
        """Removing an item should work."""
        sample_cart.add_item("Widget", 2)
        sample_cart.add_item("Gadget", 3)

        sample_cart.remove_item("Widget")

        items = sample_cart.get_items()
        assert "Widget" not in items
        assert items["Gadget"] == 3

    def test_remove_nonexistent_item(self, sample_cart):
        """Removing item not in cart should raise error."""
        with pytest.raises(ItemNotInCartError, match="not in the cart"):
            sample_cart.remove_item("Widget")

    def test_remove_invalid_item_name(self, sample_cart):
        """Invalid item names should raise error."""
        with pytest.raises(ItemNameValidationError):
            sample_cart.remove_item("Invalid@Name")


class TestGetItems:
    """Test getting cart items."""

    def test_get_empty_cart(self, sample_cart):
        """Empty cart should return empty dict."""
        items = sample_cart.get_items()
        assert items == {}

    def test_get_items(self, sample_cart):
        """Getting items should return all items."""
        sample_cart.add_item("Widget", 2)
        sample_cart.add_item("Gadget", 3)

        items = sample_cart.get_items()
        assert items == {"Widget": 2, "Gadget": 3}

    def test_defensive_copying(self, sample_cart):
        """Modifying returned items should not affect cart."""
        sample_cart.add_item("Widget", 2)

        items = sample_cart.get_items()
        items["Widget"] = 999
        items["Hacked"] = 1

        # Cart should be unchanged
        actual_items = sample_cart.get_items()
        assert actual_items["Widget"] == 2
        assert "Hacked" not in actual_items


class TestGetTotal:
    """Test total calculation."""

    def test_empty_cart_total(self, sample_cart):
        """Empty cart should have zero total."""
        assert sample_cart.get_total() == Decimal("0.00")

    def test_single_item_total(self, sample_cart):
        """Single item total should be correct."""
        sample_cart.add_item("Widget", 1)
        assert sample_cart.get_total() == Decimal("10.99")

    def test_multiple_items_total(self, sample_cart):
        """Multiple items total should be correct."""
        sample_cart.add_item("Widget", 2)  # 2 * 10.99 = 21.98
        sample_cart.add_item("Gadget", 1)  # 1 * 25.50 = 25.50
        sample_cart.add_item("Doohickey", 3)  # 3 * 5.00 = 15.00
        # Total = 62.48

        assert sample_cart.get_total() == Decimal("62.48")

    def test_decimal_precision(self, sample_cart):
        """Total should maintain decimal precision."""
        sample_cart.add_item("Widget", 3)  # 3 * 10.99 = 32.97

        total = sample_cart.get_total()
        assert total == Decimal("32.97")
        assert isinstance(total, Decimal)

    def test_total_after_update(self, sample_cart):
        """Total should update after quantity changes."""
        sample_cart.add_item("Widget", 2)
        assert sample_cart.get_total() == Decimal("21.98")

        sample_cart.update_item_quantity("Widget", 5)
        assert sample_cart.get_total() == Decimal("54.95")

    def test_total_after_remove(self, sample_cart):
        """Total should update after item removal."""
        sample_cart.add_item("Widget", 2)
        sample_cart.add_item("Gadget", 1)
        assert sample_cart.get_total() == Decimal("47.48")

        sample_cart.remove_item("Gadget")
        assert sample_cart.get_total() == Decimal("21.98")


class TestImmutability:
    """Test immutability guarantees."""

    def test_cart_id_immutable(self, sample_cart):
        """Cart ID should not be modifiable."""
        with pytest.raises(
            ImmutabilityViolationError, match="Cannot modify immutable field 'cart_id'"
        ):
            sample_cart._cart_id = uuid.uuid4()

    def test_customer_id_immutable(self, sample_cart):
        """Customer ID should not be modifiable."""
        with pytest.raises(
            ImmutabilityViolationError, match="Cannot modify immutable field 'customer_id'"
        ):
            sample_cart._customer_id = "XYZ99999ZZ-Q"

    def test_cart_id_property_readonly(self, sample_cart):
        """Cart ID property should be read-only."""
        original_id = sample_cart.cart_id

        # Trying to set via property should fail
        with pytest.raises(AttributeError):
            sample_cart.cart_id = uuid.uuid4()

        # ID should be unchanged
        assert sample_cart.cart_id == original_id

    def test_customer_id_property_readonly(self, sample_cart):
        """Customer ID property should be read-only."""
        original_id = sample_cart.customer_id

        # Trying to set via property should fail
        with pytest.raises(AttributeError):
            sample_cart.customer_id = "XYZ99999ZZ-Q"

        # ID should be unchanged
        assert sample_cart.customer_id == original_id
