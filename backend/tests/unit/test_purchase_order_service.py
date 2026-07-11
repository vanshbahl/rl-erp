"""
Unit tests for PurchaseOrderService and purchase order routes.
"""

import pytest
from unittest.mock import patch
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction


@pytest.mark.unit
class TestPurchaseOrderService:

    def test_create_po_success(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        payload = {
            "supplier_id": supplier.id,
            "contact_person": "Jane Doe",
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 10,
                    "rate": 50
                }
            ]
        }
        
        response = client.post("/purchase-orders", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["supplier_id"] == supplier.id
        assert data["status"] == "DRAFT"
        assert data["total_amount"] == 500.0
        assert data["po_number"] is not None

    def test_create_po_supplier_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_product
        product = make_product(db)
        
        payload = {
            "supplier_id": 9999,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 50}]
        }
        
        response = client.post("/purchase-orders", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "Supplier not found" in response.json()["detail"]

    def test_create_po_product_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_supplier
        supplier = make_supplier(db)
        
        payload = {
            "supplier_id": supplier.id,
            "items": [{"product_id": 9999, "quantity": 10, "rate": 50}]
        }
        
        response = client.post("/purchase-orders", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "Product 9999 not found" in response.json()["detail"]

    def test_po_numbering(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        payload = {
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }
        
        res1 = client.post("/purchase-orders", json=payload, headers=admin_headers)
        po_num_1 = res1.json()["po_number"]
        
        res2 = client.post("/purchase-orders", json=payload, headers=admin_headers)
        po_num_2 = res2.json()["po_number"]
        
        assert po_num_1 != po_num_2
        # Verify it increments correctly
        num1 = int(po_num_1.split("-")[1])
        num2 = int(po_num_2.split("-")[1])
        assert num2 == num1 + 1

    def test_list_purchase_orders(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        
        response = client.get("/purchase-orders", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_purchase_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 5, "rate": 10}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        response = client.get(f"/purchase-orders/{po_id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == po_id
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product.id
        assert data["items"][0]["quantity"] == 5

    def test_get_purchase_order_not_found(self, client, admin_headers):
        response = client.get("/purchase-orders/9999", headers=admin_headers)
        assert response.status_code == 404
        assert "Purchase order not found" in response.json()["detail"]

    def test_transition_status_success(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        response = client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)
        assert response.status_code == 200
        
        po_resp = client.get(f"/purchase-orders/{po_id}", headers=admin_headers)
        assert po_resp.json()["status"] == "SENT"

    def test_transition_status_invalid_transition(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        # DRAFT -> RECEIVED is invalid
        response = client.patch(f"/purchase-orders/{po_id}/status", json={"status": "RECEIVED"}, headers=admin_headers)
        assert response.status_code == 400
        assert "Invalid status transition" in response.json()["detail"]

    def test_transition_status_same_status(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        # DRAFT -> DRAFT
        response = client.patch(f"/purchase-orders/{po_id}/status", json={"status": "DRAFT"}, headers=admin_headers)
        assert response.status_code == 400
        assert "already in that status" in response.json()["detail"]

    def test_transition_status_unknown_status(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product, make_purchase_order
        supplier = make_supplier(db)
        po = make_purchase_order(db, supplier_id=supplier.id, status="UNKNOWN_STATUS")
        
        response = client.patch(f"/purchase-orders/{po.id}/status", json={"status": "SENT"}, headers=admin_headers)
        assert response.status_code == 400
        assert "Unknown current purchase order status" in response.json()["detail"]

    def test_transition_status_not_found(self, client, admin_headers):
        response = client.patch("/purchase-orders/9999/status", json={"status": "SENT"}, headers=admin_headers)
        assert response.status_code == 404

    def test_receive_goods_partial_then_complete(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product1 = make_product(db)
        product2 = make_product(db)
        
        # Create PO
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [
                {"product_id": product1.id, "quantity": 10, "rate": 5},
                {"product_id": product2.id, "quantity": 20, "rate": 2}
            ]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        # Transition to SENT
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)
        
        # 1. Partial Receive
        rec_resp1 = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [
                {"product_id": product1.id, "received_quantity": 4},
                {"product_id": product2.id, "received_quantity": 20}
            ]
        }, headers=admin_headers)
        
        assert rec_resp1.status_code == 200
        assert rec_resp1.json()["status"] == "PARTIALLY_RECEIVED"
        
        # Verify inventory for product1 and product2
        inv1 = db.query(Inventory).filter_by(product_id=product1.id).first()
        assert inv1.quantity == 4
        inv2 = db.query(Inventory).filter_by(product_id=product2.id).first()
        assert inv2.quantity == 20
        
        # Verify transaction logs
        txs = db.query(InventoryTransaction).filter_by(purchase_order_id=po_id).all()
        assert len(txs) == 2
        
        # 2. Complete Receive
        rec_resp2 = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [
                {"product_id": product1.id, "received_quantity": 6}
            ]
        }, headers=admin_headers)
        
        assert rec_resp2.status_code == 200
        assert rec_resp2.json()["status"] == "RECEIVED"
        
        # Verify inventory
        db.refresh(inv1)
        assert inv1.quantity == 10

    def test_receive_goods_exceed_quantity(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 5}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)
        
        # Try to receive 15 when only 10 were ordered
        response = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [{"product_id": product.id, "received_quantity": 15}]
        }, headers=admin_headers)
        
        assert response.status_code == 400
        assert "Cannot receive 15.0" in response.json()["detail"] or "Cannot receive 15" in response.json()["detail"]

    def test_receive_goods_zero_quantity(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 5}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)
        
        response = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [{"product_id": product.id, "received_quantity": 0}]
        }, headers=admin_headers)
        
        assert response.status_code == 400
        assert "greater than zero" in response.json()["detail"]

    def test_receive_goods_invalid_product(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        other_product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 5}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)
        
        response = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [{"product_id": other_product.id, "received_quantity": 5}]
        }, headers=admin_headers)
        
        assert response.status_code == 400
        assert "not part of this purchase order" in response.json()["detail"]

    def test_receive_goods_cancelled_po(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 5}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        
        response = client.post(f"/purchase-orders/{po_id}/receive", json={
            "items": [{"product_id": product.id, "received_quantity": 5}]
        }, headers=admin_headers)
        
        assert response.status_code == 400
        assert "Cannot receive a cancelled purchase order" in response.json()["detail"]

    def test_receive_goods_not_found(self, client, admin_headers):
        response = client.post("/purchase-orders/9999/receive", json={
            "items": [{"product_id": 1, "received_quantity": 5}]
        }, headers=admin_headers)
        assert response.status_code == 404

    @patch("app.services.purchase_order_service.PurchaseOrderService._generate_po_number")
    def test_create_po_concurrency_failure(self, mock_generate, client, admin_headers, db):
        # We simulate high concurrency by making _generate_po_number raise an IntegrityError
        from sqlalchemy.exc import IntegrityError
        from tests.factories.models import make_supplier, make_product
        
        supplier = make_supplier(db)
        product = make_product(db)
        
        mock_generate.side_effect = IntegrityError("mock error", params=None, orig=None)
        
        payload = {
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 50}]
        }
        
        response = client.post("/purchase-orders", json=payload, headers=admin_headers)
        assert response.status_code == 500
        assert "high concurrency" in response.json()["detail"]

    @patch("app.services.purchase_order_service.PurchaseOrderService._generate_po_number")
    def test_create_po_general_exception(self, mock_generate, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        
        supplier = make_supplier(db)
        product = make_product(db)
        
        mock_generate.side_effect = ValueError("Something else went wrong")
        
        payload = {
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 10, "rate": 50}]
        }
        
        with pytest.raises(ValueError):
            client.post("/purchase-orders", json=payload, headers=admin_headers)

    @patch("sqlalchemy.orm.Session.commit")
    def test_transition_status_exception(self, mock_commit, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product
        supplier = make_supplier(db)
        product = make_product(db)
        
        resp = client.post("/purchase-orders", json={
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }, headers=admin_headers)
        po_id = resp.json()["id"]
        
        mock_commit.side_effect = ValueError("Mock DB error")
        
        with pytest.raises(ValueError):
            client.patch(f"/purchase-orders/{po_id}/status", json={"status": "SENT"}, headers=admin_headers)

    def test_generate_po_number_invalid_format(self, client, admin_headers, db):
        from tests.factories.models import make_supplier, make_product, make_purchase_order
        supplier = make_supplier(db)
        product = make_product(db)
        
        # Create a PO with a weird format to break the po_number int() parsing
        make_purchase_order(db, supplier_id=supplier.id, po_number="PO-INVALID")
        
        # Now create a normal PO to see if it gracefully handles it and restarts numbering
        payload = {
            "supplier_id": supplier.id,
            "items": [{"product_id": product.id, "quantity": 1, "rate": 10}]
        }
        
        response = client.post("/purchase-orders", json=payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["po_number"] == "PO-000001"

