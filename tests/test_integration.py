"""Integration tests for complete shopping workflows."""

from decimal import Decimal

from shopping_cart import Catalog, ShoppingCart


class TestCompleteShoppingWorkflow:
    """Test complete shopping cart workflows end-to-end."""

    def test_basic_shopping_flow(self):
        """Complete shopping workflow with multiple items."""
        # Create catalog
        catalog = Catalog(
            {
                "Widget": Decimal("10.99"),
                "Gadget": Decimal("25.50"),
                "Doohickey": Decimal("5.00"),
                "Thingamajig": Decimal("99.99"),
            }
        )

        # Create cart
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Verify cart properties
        assert cart.customer_id == "ABC12345XY-A"
        assert cart.cart_id is not None

        # Start with empty cart
        assert cart.get_items() == {}
        assert cart.get_total() == Decimal("0.00")

        # Add items
        cart.add_item("Widget", 2)
        cart.add_item("Gadget", 1)
        cart.add_item("Doohickey", 5)

        # Verify items and total
        items = cart.get_items()
        assert items["Widget"] == 2
        assert items["Gadget"] == 1
        assert items["Doohickey"] == 5

        expected_total = Decimal("10.99") * 2 + Decimal("25.50") * 1 + Decimal("5.00") * 5
        assert cart.get_total() == expected_total  # 72.48

        # Update quantity
        cart.update_item_quantity("Widget", 5)
        assert cart.get_items()["Widget"] == 5

        new_total = Decimal("10.99") * 5 + Decimal("25.50") * 1 + Decimal("5.00") * 5
        assert cart.get_total() == new_total  # 105.45

        # Remove item
        cart.remove_item("Doohickey")
        assert "Doohickey" not in cart.get_items()

        final_total = Decimal("10.99") * 5 + Decimal("25.50") * 1
        assert cart.get_total() == final_total  # 80.45

    def test_multiple_carts_same_customer(self):
        """Multiple carts for same customer should be independent."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        cart1 = ShoppingCart("ABC12345XY-A", catalog)
        cart2 = ShoppingCart("ABC12345XY-A", catalog)

        # Same customer ID
        assert cart1.customer_id == cart2.customer_id

        # Different cart IDs
        assert cart1.cart_id != cart2.cart_id

        # Independent state
        cart1.add_item("Widget", 2)
        cart2.add_item("Widget", 5)

        assert cart1.get_items()["Widget"] == 2
        assert cart2.get_items()["Widget"] == 5
        assert cart1.get_total() == Decimal("21.98")
        assert cart2.get_total() == Decimal("54.95")

    def test_different_customers_different_carts(self):
        """Different customers should have separate carts."""
        catalog = Catalog({"Widget": Decimal("10.99")})

        cart_a = ShoppingCart("ABC12345XY-A", catalog)
        cart_q = ShoppingCart("XYZ99999ZZ-Q", catalog)

        assert cart_a.customer_id == "ABC12345XY-A"
        assert cart_q.customer_id == "XYZ99999ZZ-Q"
        assert cart_a.cart_id != cart_q.cart_id

        cart_a.add_item("Widget", 3)
        cart_q.add_item("Widget", 7)

        assert cart_a.get_items()["Widget"] == 3
        assert cart_q.get_items()["Widget"] == 7

    def test_incremental_quantity_updates(self):
        """Adding same item multiple times should accumulate."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        cart.add_item("Widget", 1)
        assert cart.get_items()["Widget"] == 1

        cart.add_item("Widget", 2)
        assert cart.get_items()["Widget"] == 3

        cart.add_item("Widget", 3)
        assert cart.get_items()["Widget"] == 6

        assert cart.get_total() == Decimal("10.99") * 6  # 65.94

    def test_complex_decimal_arithmetic(self):
        """Complex calculations should maintain decimal precision."""
        catalog = Catalog(
            {
                "Item1": Decimal("10.99"),
                "Item2": Decimal("25.49"),
                "Item3": Decimal("5.01"),
                "Item4": Decimal("99.99"),
            }
        )

        cart = ShoppingCart("ABC12345XY-A", catalog)

        cart.add_item("Item1", 3)  # 32.97
        cart.add_item("Item2", 2)  # 50.98
        cart.add_item("Item3", 7)  # 35.07
        cart.add_item("Item4", 1)  # 99.99

        total = cart.get_total()
        expected = Decimal("219.01")

        assert total == expected
        assert isinstance(total, Decimal)

    def test_empty_cart_operations(self):
        """Operations on empty cart should work correctly."""
        catalog = Catalog({"Widget": Decimal("10.99")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Empty cart
        assert cart.get_items() == {}
        assert cart.get_total() == Decimal("0.00")

        # Add and remove to make empty again
        cart.add_item("Widget", 1)
        cart.remove_item("Widget")

        assert cart.get_items() == {}
        assert cart.get_total() == Decimal("0.00")

    def test_large_catalog_operations(self):
        """Cart should handle large catalogs efficiently."""
        # Create catalog with many items
        catalog_items = {f"Item-{i}": Decimal(f"{i}.99") for i in range(1, 101)}
        catalog = Catalog(catalog_items)

        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Add multiple items
        for i in range(1, 21):
            cart.add_item(f"Item-{i}", 1)

        # Verify all items added
        items = cart.get_items()
        assert len(items) == 20

        # Verify total
        expected_total = sum(Decimal(f"{i}.99") for i in range(1, 21))
        assert cart.get_total() == expected_total

    def test_cart_modification_sequence(self):
        """Complex sequence of modifications should maintain consistency."""
        catalog = Catalog(
            {
                "Widget": Decimal("10.00"),
                "Gadget": Decimal("20.00"),
                "Doohickey": Decimal("30.00"),
            }
        )

        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Add items
        cart.add_item("Widget", 2)  # 20.00
        cart.add_item("Gadget", 3)  # 60.00
        assert cart.get_total() == Decimal("80.00")

        # Update quantity
        cart.update_item_quantity("Widget", 5)  # 50.00
        assert cart.get_total() == Decimal("110.00")

        # Add more
        cart.add_item("Doohickey", 1)  # 30.00
        assert cart.get_total() == Decimal("140.00")

        # Remove one
        cart.remove_item("Gadget")
        assert cart.get_total() == Decimal("80.00")

        # Add to existing
        cart.add_item("Widget", 5)  # Total 10 widgets = 100.00
        assert cart.get_total() == Decimal("130.00")

        # Final state
        final_items = cart.get_items()
        assert final_items == {"Widget": 10, "Doohickey": 1}
        assert cart.get_total() == Decimal("130.00")

    def test_boundary_quantity_operations(self):
        """Operations at quantity boundaries should work correctly."""
        catalog = Catalog({"Widget": Decimal("1.00")})
        cart = ShoppingCart("ABC12345XY-A", catalog)

        # Minimum quantity
        cart.add_item("Widget", 1)
        assert cart.get_items()["Widget"] == 1

        # Maximum quantity
        cart.update_item_quantity("Widget", 10000)
        assert cart.get_items()["Widget"] == 10000
        assert cart.get_total() == Decimal("10000.00")

    def test_realistic_shopping_scenario(self):
        """Realistic shopping scenario with mixed operations."""
        # Setup: Online store catalog
        catalog = Catalog(
            {
                "Laptop": Decimal("999.99"),
                "Mouse": Decimal("25.99"),
                "Keyboard": Decimal("79.99"),
                "Monitor": Decimal("299.99"),
                "USB Cable": Decimal("9.99"),
                "Laptop Bag": Decimal("49.99"),
            }
        )

        # Customer creates cart
        cart = ShoppingCart("TEC12345AB-Q", catalog)

        # Customer adds laptop and accessories
        cart.add_item("Laptop", 1)
        cart.add_item("Mouse", 1)
        cart.add_item("Keyboard", 1)

        # Customer decides to add monitor
        cart.add_item("Monitor", 1)

        # Customer adds multiple USB cables
        cart.add_item("USB Cable", 3)

        # Check total so far
        subtotal = (
            Decimal("999.99")
            + Decimal("25.99")
            + Decimal("79.99")
            + Decimal("299.99")
            + Decimal("9.99") * 3
        )
        assert cart.get_total() == subtotal  # 1435.93

        # Customer changes mind about monitor
        cart.remove_item("Monitor")

        # Customer adds laptop bag
        cart.add_item("Laptop Bag", 1)

        # Final total
        final_total = (
            Decimal("999.99")
            + Decimal("25.99")
            + Decimal("79.99")
            + Decimal("9.99") * 3
            + Decimal("49.99")
        )
        assert cart.get_total() == final_total  # 1185.93

        # Verify final items
        final_items = cart.get_items()
        assert final_items == {
            "Laptop": 1,
            "Mouse": 1,
            "Keyboard": 1,
            "USB Cable": 3,
            "Laptop Bag": 1,
        }
