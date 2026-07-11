"""
Unit tests for InventoryService.

Coverage targets:
- get_inventory: returns all inventory records
- get_low_stock: returns records where quantity <= minimum_stock
- get_low_stock: product_type filter applied correctly
- get_low_stock: supplier_id filter applied correctly
- get_inventory_item: 404 when product has no inventory record
- create_inventory: duplicate prevention (one record per product)
- update_inventory: quantity and minimum_stock updated correctly
"""

import pytest

pytestmark = pytest.mark.unit
