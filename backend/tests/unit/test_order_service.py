"""
Unit tests for OrderService and order routes.

Coverage targets:
- Create order (success, missing customer, missing product)
- Dispatch (success, missing inventory, insufficient inventory)
- Cancel (success from PENDING, success from DISPATCHED with restoration)
- Complete (success from DISPATCHED)
- Invalid transitions (e.g., PENDING -> COMPLETED)
- Duplicate transitions (e.g., DISPATCHED -> DISPATCHED)
- Inventory deduction & restoration
- Transaction logging
- Completed order protection
"""

import pytest
from app.models.order import Order
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction


@pytest.mark.unit
class TestOrderService:

    def test_create_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product
        customer = make_customer(db)
        product = make_product(db)
        
        payload = {
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "contact_person": "John Doe",
            "po_number": "PO-001",
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 5,
                    "rate": 100
                }
            ]
        }
        
        response = client.post("/orders/", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Order created successfully"
        assert data["status"] == "PENDING"
        assert data["total_amount"] == 500.0

    def test_create_order_customer_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_product
        product = make_product(db)
        
        payload = {
            "customer_id": 9999,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 5, "rate": 100}]
        }
        
        response = client.post("/orders/", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"

    def test_create_order_product_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_customer
        customer = make_customer(db)
        
        payload = {
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "contact_person": "John Doe",
            "items": [{"product_id": 9999, "quantity": 5, "rate": 100}]
        }
        
        response = client.post("/orders/", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "Product 9999 not found" in response.json()["detail"]

    def test_get_orders(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product
        customer = make_customer(db)
        product = make_product(db)
        
        client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        
        response = client.get("/orders/", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product
        customer = make_customer(db)
        product = make_product(db)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        response = client.get(f"/orders/{order_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["order_id"] == order_id
        assert len(response.json()["items"]) == 1

    def test_get_order_not_found(self, client, admin_headers):
        response = client.get("/orders/9999", headers=admin_headers)
        assert response.status_code == 404

    def test_dispatch_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        inv = make_inventory(db, product_id=product.id, quantity=50)
        
        # Create order
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        # Transition PENDING -> PROCESSING
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        
        # Transition PROCESSING -> DISPATCHED
        response = client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "DISPATCHED"
        
        # Verify inventory deduction
        db.refresh(inv)
        assert inv.quantity == 40
        
        # Verify transaction logging
        transaction = db.query(InventoryTransaction).filter_by(order_id=order_id, transaction_type="ORDER_DISPATCH").first()
        assert transaction is not None
        assert transaction.quantity_change == -10
        assert transaction.product_id == product.id

    def test_dispatch_missing_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product
        customer = make_customer(db)
        product = make_product(db)
        # Note: We deliberately DO NOT create inventory for this product
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        
        response = client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        assert response.status_code == 404
        assert "Inventory not found" in response.json()["detail"]

    def test_dispatch_insufficient_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        make_inventory(db, product_id=product.id, quantity=5) # Only 5 available
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}] # Trying to dispatch 10
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        
        response = client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        assert response.status_code == 400
        assert "Insufficient inventory" in response.json()["detail"]

    def test_cancel_order_from_dispatched_restores_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        inv = make_inventory(db, product_id=product.id, quantity=50)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers) # Deducts 10 -> 40
        
        # Now cancel from DISPATCHED
        response = client.patch(f"/orders/{order_id}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        assert response.status_code == 200
        
        # Verify restoration
        db.refresh(inv)
        assert inv.quantity == 50
        
        # Verify transaction
        transaction = db.query(InventoryTransaction).filter_by(order_id=order_id, transaction_type="ORDER_CANCEL").first()
        assert transaction is not None
        assert transaction.quantity_change == 10

    def test_cancel_dispatched_order_missing_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        inv = make_inventory(db, product_id=product.id, quantity=50)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        
        # Delete inventory manually to trigger the missing inventory check during cancel
        db.delete(inv)
        db.commit()
        
        response = client.patch(f"/orders/{order_id}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        assert response.status_code == 404
        assert "Inventory not found" in response.json()["detail"]

    def test_complete_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        make_inventory(db, product_id=product.id, quantity=50)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        
        # Complete
        response = client.patch(f"/orders/{order_id}/status", json={"status": "COMPLETED"}, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

    def test_invalid_transitions(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product
        customer = make_customer(db)
        product = make_product(db)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        # PENDING -> COMPLETED should be invalid
        response = client.patch(f"/orders/{order_id}/status", json={"status": "COMPLETED"}, headers=admin_headers)
        assert response.status_code == 400
        assert "is not allowed" in response.json()["detail"]
        
        # PENDING -> PENDING (Duplicate)
        response = client.patch(f"/orders/{order_id}/status", json={"status": "PENDING"}, headers=admin_headers)
        assert response.status_code == 400
        assert "already in that status" in response.json()["detail"]

    def test_completed_order_protection(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_inventory
        customer = make_customer(db)
        product = make_product(db)
        make_inventory(db, product_id=product.id, quantity=50)
        
        resp = client.post("/orders/", json={
            "customer_id": customer.id,
            "contact_person": "John Doe",
            "items": [{"product_id": product.id, "quantity": 10, "rate": 100}]
        }, headers=admin_headers)
        order_id = resp.json()["order_id"]
        
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "COMPLETED"}, headers=admin_headers)
        
        # Attempt to cancel completed
        response = client.patch(f"/orders/{order_id}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    def test_transition_order_not_found(self, client, admin_headers):
        response = client.patch("/orders/9999/status", json={"status": "PROCESSING"}, headers=admin_headers)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
