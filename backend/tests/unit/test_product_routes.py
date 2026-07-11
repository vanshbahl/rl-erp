"""
Unit tests for Product routes.

Coverage targets:
- Create product (success, duplicate SKU, invalid type)
- Get all products
- Get single product (success, not found)
- Update product (success, not found)
- Deactivate product (success, not found)
- Delete product (success, not found)
"""

import pytest
from app.models.product import Product
from app.models.inventory import Inventory


@pytest.mark.unit
class TestProductRoutes:

    def test_create_product_success(self, client, admin_headers, db):
        payload = {
            "name": "Widget A",
            "sku": "WIDGET-A-001",
            "product_type": "FINISHED_GOOD",
            "standard_cost": 10.5
        }
        response = client.post("/products/", json=payload, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Widget A"
        assert data["sku"] == "WIDGET-A-001"
        assert "id" in data
        
        # Verify product created
        product = db.query(Product).filter(Product.id == data["id"]).first()
        assert product is not None
        
        # Verify initial inventory created automatically
        inventory = db.query(Inventory).filter(Inventory.product_id == data["id"]).first()
        assert inventory is not None
        assert inventory.quantity == 0

    def test_create_product_duplicate_sku(self, client, admin_headers, db):
        from tests.factories.models import make_product
        make_product(db, sku="DUP-SKU-1", name="Original")

        payload = {
            "name": "Duplicate",
            "sku": "DUP-SKU-1",
            "product_type": "FINISHED_GOOD",
            "standard_cost": 5.0
        }
        
        # Database should throw IntegrityError, route catches it and re-raises (or FastAPI catches)
        # wait, the route in product.py does `try: ... except Exception: db.rollback(); raise`
        # which means it will raise a 500 error unhandled by FastAPI unless there's a global handler.
        # So we expect 500 for duplicate SKU based on the current code.
        with pytest.raises(Exception):
            client.post("/products/", json=payload, headers=admin_headers)

    def test_create_product_invalid_type(self, client, admin_headers):
        payload = {
            "name": "Widget B",
            "sku": "WIDGET-B-001",
            "product_type": "INVALID_TYPE",
            "standard_cost": 10.5
        }
        response = client.post("/products/", json=payload, headers=admin_headers)
        
        # Pydantic validation error expected
        assert response.status_code == 422

    def test_get_products(self, client, db):
        from tests.factories.models import make_product
        make_product(db, name="Active 1", is_active=True)
        make_product(db, name="Active 2", is_active=True)
        make_product(db, name="Inactive 1", is_active=False)
        
        response = client.get("/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        # Ensure only active products are returned
        assert all(p["is_active"] for p in data)

    def test_get_product_success(self, client, db):
        from tests.factories.models import make_product
        prod = make_product(db, name="Target Product")
        
        response = client.get(f"/products/{prod.id}")
        
        assert response.status_code == 200
        assert response.json()["name"] == "Target Product"

    def test_get_product_not_found(self, client):
        response = client.get("/products/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_update_product_success(self, client, admin_headers, db):
        from tests.factories.models import make_product
        prod = make_product(db, name="Old Name")
        
        payload = {"name": "New Name", "sku": prod.sku, "standard_cost": 25.0}
        response = client.put(f"/products/{prod.id}", json=payload, headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        
        db.refresh(prod)
        assert prod.name == "New Name"

    def test_update_product_not_found(self, client, admin_headers):
        payload = {"name": "New Name", "sku": "SOME-SKU", "standard_cost": 25.0}
        response = client.put("/products/999999", json=payload, headers=admin_headers)
        assert response.status_code == 404

    def test_deactivate_product_success(self, client, admin_headers, db):
        from tests.factories.models import make_product
        prod = make_product(db, is_active=True)
        
        response = client.patch(f"/products/{prod.id}/deactivate", headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json()["product"]["is_active"] is False
        
        db.refresh(prod)
        assert prod.is_active is False

    def test_deactivate_product_not_found(self, client, admin_headers):
        response = client.patch("/products/999999/deactivate", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_product_success(self, client, admin_headers, db):
        from tests.factories.models import make_product
        prod = make_product(db)
        prod_id = prod.id
        
        response = client.delete(f"/products/{prod_id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert db.query(Product).filter(Product.id == prod_id).first() is None

    def test_delete_product_not_found(self, client, admin_headers):
        response = client.delete("/products/999999", headers=admin_headers)
        assert response.status_code == 404
