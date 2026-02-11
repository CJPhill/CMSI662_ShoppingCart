"""Tests for catalog implementation."""

from decimal import Decimal

import pytest

from shopping_cart.catalog import Catalog, CatalogItem
from shopping_cart.exceptions import ItemNameValidationError, PriceValidationError


class TestCatalogItem:
    """Test CatalogItem frozen dataclass."""

    def test_create_valid_item(self):
        """Valid items should be created successfully."""
        item = CatalogItem(name="Widget", price=Decimal("10.99"))
        assert item.name == "Widget"
        assert item.price == Decimal("10.99")

    def test_immutability(self):
        """CatalogItem should be immutable."""
        item = CatalogItem(name="Widget", price=Decimal("10.99"))

        with pytest.raises(AttributeError):
            item.name = "Gadget"

        with pytest.raises(AttributeError):
            item.price = Decimal("20.00")

    def test_validation_on_creation(self):
        """Invalid items should raise validation errors."""
        # Invalid name
        with pytest.raises(ItemNameValidationError):
            CatalogItem(name="Invalid@Name", price=Decimal("10.99"))

        # Invalid price
        with pytest.raises(PriceValidationError):
            CatalogItem(name="Widget", price=Decimal("-1.00"))


class TestCatalog:
    """Test Catalog class."""

    def test_create_catalog(self):
        """Catalog should be created with valid items."""
        items = {
            "Widget": Decimal("10.99"),
            "Gadget": Decimal("25.50"),
        }
        catalog = Catalog(items)
        assert catalog.has_item("Widget")
        assert catalog.has_item("Gadget")

    def test_has_item(self):
        """has_item should correctly identify items."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        assert catalog.has_item("Widget") is True
        assert catalog.has_item("Nonexistent") is False
        assert catalog.has_item("Gadget") is False

    def test_get_price(self):
        """get_price should return correct prices."""
        catalog = Catalog(
            {
                "Widget": Decimal("10.99"),
                "Gadget": Decimal("25.50"),
            }
        )

        assert catalog.get_price("Widget") == Decimal("10.99")
        assert catalog.get_price("Gadget") == Decimal("25.50")
        assert catalog.get_price("Nonexistent") is None

    def test_get_all_items(self):
        """get_all_items should return all items."""
        items = {
            "Widget": Decimal("10.99"),
            "Gadget": Decimal("25.50"),
        }
        catalog = Catalog(items)
        all_items = catalog.get_all_items()

        assert all_items == items
        assert len(all_items) == 2

    def test_defensive_copying(self):
        """Modifying returned data should not affect catalog."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        # Get items and modify
        items = catalog.get_all_items()
        items["Hacked"] = Decimal("0.01")
        items["Widget"] = Decimal("999.99")

        # Catalog should be unchanged
        assert catalog.has_item("Hacked") is False
        assert catalog.get_price("Widget") == Decimal("10.99")

    def test_validation_on_creation(self):
        """Invalid items should raise errors during catalog creation."""
        # Invalid item name
        with pytest.raises(ItemNameValidationError):
            Catalog({"Invalid@Name": Decimal("10.99")})

        # Invalid price
        with pytest.raises(PriceValidationError):
            Catalog({"Widget": Decimal("-1.00")})

        # Too many decimal places
        with pytest.raises(PriceValidationError):
            Catalog({"Widget": Decimal("10.999")})

    def test_empty_catalog(self):
        """Empty catalog should work correctly."""
        catalog = Catalog({})

        assert catalog.has_item("Widget") is False
        assert catalog.get_price("Widget") is None
        assert catalog.get_all_items() == {}

    def test_catalog_immutability_attempt(self):
        """Attempting to modify catalog through returned data should fail."""
        catalog = Catalog(
            {
                "Widget": Decimal("10.99"),
                "Gadget": Decimal("25.50"),
            }
        )

        # Get items multiple times
        items1 = catalog.get_all_items()
        items2 = catalog.get_all_items()

        # Modify first copy
        items1["Widget"] = Decimal("999.99")
        items1["Hacked"] = Decimal("0.01")

        # Second copy should be unchanged (proves deep copy)
        assert items2["Widget"] == Decimal("10.99")
        assert "Hacked" not in items2

        # Catalog itself should be unchanged
        assert catalog.get_price("Widget") == Decimal("10.99")
        assert catalog.has_item("Hacked") is False
