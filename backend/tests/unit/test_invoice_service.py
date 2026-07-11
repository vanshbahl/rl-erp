"""
Unit tests for InvoiceService.
"""

import pytest
from unittest.mock import patch
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
class TestInvoiceService:
    def test_generate_invoice_success(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_product, make_order, make_order_item
        customer = make_customer(db)
        product = make_product(db)
        order = make_order(db, customer_id=customer.id, status="DISPATCHED", total_amount=150.0)
        make_order_item(db, order_id=order.id, product_id=product.id, quantity=1.0, rate=150.0)

        response = client.post(f"/invoices/generate/{order.id}?due_days=30", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_number"].startswith("INV-")

    def test_generate_invoice_invalid_due_days(self, client, admin_headers, db):
        response = client.post("/invoices/generate/1?due_days=0", headers=admin_headers)
        assert response.status_code == 400
        assert "greater than zero" in response.json()["detail"].lower()

    def test_generate_invoice_order_not_found(self, client, admin_headers):
        response = client.post("/invoices/generate/9999?due_days=30", headers=admin_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_generate_invoice_invalid_order_status(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id, status="PENDING")
        
        response = client.post(f"/invoices/generate/{order.id}?due_days=30", headers=admin_headers)
        assert response.status_code == 400
        assert "dispatched or completed" in response.json()["detail"].lower()

    def test_generate_invoice_duplicate(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id, status="DISPATCHED")
        make_invoice(db, order_id=order.id, customer_id=customer.id)
        
        response = client.post(f"/invoices/generate/{order.id}?due_days=30", headers=admin_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_generate_invoice_number_sequencing(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order1 = make_order(db, customer_id=customer.id, status="DISPATCHED")
        order2 = make_order(db, customer_id=customer.id, status="DISPATCHED")
        make_invoice(db, order_id=order2.id, customer_id=customer.id, invoice_number="INV-000042")
        
        response = client.post(f"/invoices/generate/{order1.id}?due_days=30", headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json()["invoice_number"] == "INV-000043"

    def test_generate_invoice_number_fallback(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order1 = make_order(db, customer_id=customer.id, status="DISPATCHED")
        order2 = make_order(db, customer_id=customer.id, status="DISPATCHED")
        make_invoice(db, order_id=order2.id, customer_id=customer.id, invoice_number="INVALID")
        
        response = client.post(f"/invoices/generate/{order1.id}?due_days=30", headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json()["invoice_number"] == "INV-000001"

    def test_generate_invoice_concurrency_error(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id, status="DISPATCHED")
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = IntegrityError("statement", "params", "orig")
            response = client.post(f"/invoices/generate/{order.id}?due_days=30", headers=admin_headers)
            assert response.status_code == 500
            assert "high concurrency" in response.json()["detail"].lower()

    def test_generate_invoice_exception(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id, status="DISPATCHED")
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.post(f"/invoices/generate/{order.id}?due_days=30", headers=admin_headers)

    def test_list_and_get_invoices(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        make_invoice(db, order_id=order.id, customer_id=customer.id)
        
        list_res = client.get("/invoices", headers=admin_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        
        invoice_id = list_res.json()[0]["id"]
        get_res = client.get(f"/invoices/{invoice_id}", headers=admin_headers)
        assert get_res.status_code == 200
        assert get_res.json()["invoice"]["id"] == invoice_id
        
        get_fail = client.get("/invoices/9999", headers=admin_headers)
        assert get_fail.status_code == 404

    def test_transition_status(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="DRAFT")
        
        # DRAFT -> ISSUED
        res = client.patch(f"/invoices/{invoice.id}/status", json={"status": "ISSUED"}, headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["invoice"]["status"] == "ISSUED"
        
        # ISSUED -> PARTIALLY_PAID
        res2 = client.patch(f"/invoices/{invoice.id}/status", json={"status": "PARTIALLY_PAID"}, headers=admin_headers)
        assert res2.status_code == 200
        assert res2.json()["invoice"]["status"] == "PARTIALLY_PAID"

        # PARTIALLY_PAID -> PAID
        res3 = client.patch(f"/invoices/{invoice.id}/status", json={"status": "PAID"}, headers=admin_headers)
        assert res3.status_code == 200
        assert res3.json()["invoice"]["status"] == "PAID"

        # PAID -> CANCELLED (Invalid)
        res4 = client.patch(f"/invoices/{invoice.id}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        assert res4.status_code == 400
        assert "invalid status transition" in res4.json()["detail"].lower()

    def test_transition_status_invalid_states(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="DRAFT")
        
        res = client.patch(f"/invoices/{invoice.id}/status", json={"status": "INVALID"}, headers=admin_headers)
        assert res.status_code == 400
        
        # Test unknown current status
        invoice.status = "UNKNOWN"
        db.commit()
        res_current = client.patch(f"/invoices/{invoice.id}/status", json={"status": "ISSUED"}, headers=admin_headers)
        assert res_current.status_code == 400
        assert "unknown current invoice status" in res_current.json()["detail"].lower()

    def test_transition_status_same_state(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="DRAFT")
        
        res = client.patch(f"/invoices/{invoice.id}/status", json={"status": "DRAFT"}, headers=admin_headers)
        assert res.status_code == 400
        assert "already in that status" in res.json()["detail"].lower()

    def test_transition_status_not_found(self, client, admin_headers):
        res = client.patch("/invoices/9999/status", json={"status": "ISSUED"}, headers=admin_headers)
        assert res.status_code == 404

    def test_transition_status_exception(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="DRAFT")
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.patch(f"/invoices/{invoice.id}/status", json={"status": "ISSUED"}, headers=admin_headers)
