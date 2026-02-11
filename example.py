#!/usr/bin/env python3
"""Example usage of the secure shopping cart library."""

from decimal import Decimal
from shopping_cart import Catalog, ShoppingCart


def main():
    """Demonstrate shopping cart functionality."""
    print("=" * 60)
    print("Shopping Cart Library - Secure Implementation Demo")
    print("=" * 60)
    print()

    # Create a product catalog
    print("Creating product catalog...")
    catalog = Catalog({
        "Laptop": Decimal("999.99"),
        "Mouse": Decimal("25.99"),
        "Keyboard": Decimal("79.99"),
        "Monitor": Decimal("299.99"),
        "USB Cable": Decimal("9.99"),
        "Laptop Bag": Decimal("49.99"),
    })
    print(f"Catalog created with {len(catalog.get_all_items())} items")
    print()

    # Create a shopping cart
    print("Creating shopping cart for customer TEC12345AB-Q...")
    cart = ShoppingCart("TEC12345AB-Q", catalog)
    print(f"Cart ID: {cart.cart_id}")
    print(f"Customer ID: {cart.customer_id}")
    print()

    # Add items
    print("Adding items to cart...")
    cart.add_item("Laptop", 1)
    print("  + 1x Laptop")
    cart.add_item("Mouse", 2)
    print("  + 2x Mouse")
    cart.add_item("Keyboard", 1)
    print("  + 1x Keyboard")
    print()

    # Show current cart
    print("Current cart contents:")
    items = cart.get_items()
    for item_name, quantity in items.items():
        price = catalog.get_price(item_name)
        print(f"  {item_name}: {quantity} @ ${price} = ${price * quantity}")
    print(f"Total: ${cart.get_total()}")
    print()

    # Update quantity
    print("Updating mouse quantity to 1...")
    cart.update_item_quantity("Mouse", 1)
    print(f"New total: ${cart.get_total()}")
    print()

    # Add more items
    print("Adding monitor and USB cables...")
    cart.add_item("Monitor", 1)
    cart.add_item("USB Cable", 3)
    print(f"New total: ${cart.get_total()}")
    print()

    # Remove an item
    print("Removing monitor...")
    cart.remove_item("Monitor")
    print(f"New total: ${cart.get_total()}")
    print()

    # Final cart
    print("=" * 60)
    print("FINAL CART:")
    print("=" * 60)
    final_items = cart.get_items()
    for item_name, quantity in final_items.items():
        price = catalog.get_price(item_name)
        line_total = price * quantity
        print(f"  {item_name:20s} {quantity:3d} x ${price:8.2f} = ${line_total:8.2f}")
    print("-" * 60)
    print(f"  {'TOTAL':20s}                     ${cart.get_total():8.2f}")
    print("=" * 60)
    print()

    # Demonstrate immutability
    print("Security Features Demonstration:")
    print("-" * 60)
    print("1. Cart ID and Customer ID are immutable")
    print(f"   Cart ID: {cart.cart_id}")
    print(f"   Customer ID: {cart.customer_id}")
    print()

    print("2. Defensive copying prevents indirect modification")
    items_copy = cart.get_items()
    items_copy["Hacked Item"] = 999
    print(f"   Attempted to add 'Hacked Item' via returned dict")
    print(f"   Cart still has {len(cart.get_items())} items (unchanged)")
    print()

    print("3. Input validation prevents attacks")
    print("   - Only catalog items can be added")
    print("   - Quantities must be 1-10,000")
    print("   - Item names validated (alphanumeric + space + hyphen)")
    print("   - Customer ID validated (XXX#####XX-[A|Q])")
    print()

    print("4. Decimal precision for accurate calculations")
    print(f"   Total uses Decimal type: {type(cart.get_total()).__name__}")
    print(f"   No floating-point errors: ${cart.get_total()}")
    print()

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
