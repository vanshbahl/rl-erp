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
- update_inventory: 404 when record not found
"""

import pytest
from app.models.inventory import Inventory
from app.models.product import Product

@pytest.mark.unit
class TestInventoryService:

    def test_get_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory
        p1 = make_product(db)
        p2 = make_product(db)
        make_inventory(db, product_id=p1.id)
        make_inventory(db, product_id=p2.id)
        
        response = client.get("/inventory/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_low_stock(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory
        p1 = make_product(db, product_type="RAW_MATERIAL")
        p2 = make_product(db, product_type="FINISHED_GOOD")
        
        # Low stock
        make_inventory(db, product_id=p1.id, quantity=5, minimum_stock=10)
        # Sufficient stock
        make_inventory(db, product_id=p2.id, quantity=20, minimum_stock=10)
        
        response = client.get("/inventory/low-stock", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Ensure only the low stock item is returned
        assert any(item["product_id"] == p1.id for item in data)
        assert not any(item["product_id"] == p2.id for item in data)

    def test_get_low_stock_with_filters(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory, make_supplier
        supplier = make_supplier(db)
        p1 = make_product(db, product_type="RAW_MATERIAL")
        p1.default_supplier_id = supplier.id
        db.commit() # Save changes to product
        
        make_inventory(db, product_id=p1.id, quantity=5, minimum_stock=10)
        
        # Filter by product_type
        response = client.get("/inventory/low-stock?product_type=RAW_MATERIAL", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1
        
        response_empty = client.get("/inventory/low-stock?product_type=FINISHED_GOOD", headers=admin_headers)
        assert response_empty.status_code == 200
        assert len(response_empty.json()) == 0
        
        # Filter by supplier_id
        response_supplier = client.get(f"/inventory/low-stock?supplier_id={supplier.id}", headers=admin_headers)
        assert response_supplier.status_code == 200
        assert len(response_supplier.json()) >= 1

    def test_get_inventory_item_success(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory
        p = make_product(db)
        make_inventory(db, product_id=p.id, quantity=50)
        
        response = client.get(f"/inventory/{p.id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json()["quantity"] == 50

    def test_get_inventory_item_not_found(self, client, admin_headers):
        response = client.get("/inventory/999999", headers=admin_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Inventory record not found"

    def test_create_inventory_success(self, client, admin_headers, db):
        from tests.factories.models import make_product
        p = make_product(db) # Does not have inventory yet
        
        payload = {
            "product_id": p.id,
            "quantity": 100,
            "minimum_stock": 20
        }
        
        response = client.post("/inventory/", json=payload, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 100
        assert data["minimum_stock"] == 20

    def test_create_inventory_duplicate(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory
        p = make_product(db)
        make_inventory(db, product_id=p.id) # Create initial inventory
        
        payload = {
            "product_id": p.id,
            "quantity": 100,
            "minimum_stock": 20
        }
        
        response = client.post("/inventory/", json=payload, headers=admin_headers)
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Inventory record already exists"

    def test_update_inventory_success(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_inventory
        p = make_product(db)
        inv = make_inventory(db, product_id=p.id, quantity=10, minimum_stock=5)
        
        payload = {
            "quantity": 25,
            "minimum_stock": 10
        }
        
        response = client.put(f"/inventory/{p.id}", json=payload, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 25
        assert data["minimum_stock"] == 10
        
        db.refresh(inv)
        assert inv.quantity == 25

    def test_update_inventory_not_found(self, client, admin_headers):
        payload = {
            "quantity": 25,
            "minimum_stock": 10
        }
        response = client.put("/inventory/999999", json=payload, headers=admin_headers)
        assert response.status_code == 404
