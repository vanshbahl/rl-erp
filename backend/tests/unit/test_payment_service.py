"""
Unit tests for PaymentService.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
class TestPaymentService:
    def test_create_payment_success_partial(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 40.0,
            "payment_method": "BANK_TRANSFER",
            "reference_number": "TXN123",
            "remarks": "First half"
        }
        
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_id"] == invoice.id
        assert data["amount"] == 40.0
        
        db.refresh(invoice)
        assert invoice.status == "PARTIALLY_PAID"

    def test_create_payment_success_full(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="PARTIALLY_PAID", total_amount=100.0)
        make_payment(db, invoice_id=invoice.id, amount=40.0)
        
        payload = {
            "invoice_id": invoice.id,
            "amount": 60.0,
            "payment_method": "CASH",
            "reference_number": "",
            "remarks": "Final half"
        }
        
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 200
        
        db.refresh(invoice)
        assert invoice.status == "PAID"

    def test_create_payment_invoice_not_found(self, client, admin_headers):
        payload = {
            "invoice_id": 9999,
            "amount": 40.0,
            "payment_method": "BANK_TRANSFER"
        }
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_payment_invalid_invoice_status(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="DRAFT", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 40.0,
            "payment_method": "BANK_TRANSFER"
        }
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "cannot record payment" in response.json()["detail"].lower()

    def test_create_payment_invalid_amount(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 0.0,
            "payment_method": "BANK_TRANSFER"
        }
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "greater than zero" in response.json()["detail"].lower()

    def test_create_payment_invalid_method(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 40.0,
            "payment_method": "BITCOIN"
        }
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "payment method must be one of" in response.json()["detail"].lower()

    def test_create_payment_overpayment(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 100.01,
            "payment_method": "BANK_TRANSFER"
        }
        response = client.post("/payments", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "exceeds outstanding balance" in response.json()["detail"].lower()

    def test_create_payment_exception(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)

        payload = {
            "invoice_id": invoice.id,
            "amount": 40.0,
            "payment_method": "BANK_TRANSFER"
        }
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Error")
            with pytest.raises(ValueError):
                client.post("/payments", json=payload, headers=admin_headers)

    def test_list_and_get_payments(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)
        payment = make_payment(db, invoice_id=invoice.id, amount=10.0)

        list_res = client.get("/payments", headers=admin_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        
        get_res = client.get(f"/payments/{payment.id}", headers=admin_headers)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == payment.id
        
        get_fail = client.get("/payments/9999", headers=admin_headers)
        assert get_fail.status_code == 404

    def test_invoice_summary(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)
        make_payment(db, invoice_id=invoice.id, amount=10.0)

        res = client.get(f"/payments/invoice/{invoice.id}/summary", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["invoice_total"] == 100.0
        assert data["paid_amount"] == 10.0
        assert data["outstanding_amount"] == 90.0

        res_fail = client.get("/payments/invoice/9999/summary", headers=admin_headers)
        assert res_fail.status_code == 404

    def test_customer_summary_and_invoices(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order1 = make_order(db, customer_id=customer.id)
        order2 = make_order(db, customer_id=customer.id)
        invoice1 = make_invoice(db, order_id=order1.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)
        invoice2 = make_invoice(db, order_id=order2.id, customer_id=customer.id, status="PARTIALLY_PAID", total_amount=50.0)
        make_payment(db, invoice_id=invoice1.id, amount=10.0)

        # Customer Summary
        res_summary = client.get(f"/payments/customer/{customer.id}/summary", headers=admin_headers)
        assert res_summary.status_code == 200
        data_summary = res_summary.json()
        assert data_summary["total_invoiced"] == 150.0
        assert data_summary["total_paid"] == 10.0
        assert data_summary["outstanding_amount"] == 140.0

        # Customer Invoices
        res_invoices = client.get(f"/payments/customer/{customer.id}/invoices", headers=admin_headers)
        assert res_invoices.status_code == 200
        data_invoices = res_invoices.json()["invoices"]
        assert len(data_invoices) == 2
        
        # Not found testing
        res_fail = client.get("/payments/customer/9999/summary", headers=admin_headers)
        assert res_fail.status_code == 404
        res_fail_2 = client.get("/payments/customer/9999/invoices", headers=admin_headers)
        assert res_fail_2.status_code == 404

    def test_customer_summary_no_invoices(self, client, admin_headers, db):
        from tests.factories.models import make_customer
        customer = make_customer(db)
        
        res_summary = client.get(f"/payments/customer/{customer.id}/summary", headers=admin_headers)
        assert res_summary.status_code == 200
        data_summary = res_summary.json()
        assert data_summary["total_invoiced"] == 0.0
        assert data_summary["total_paid"] == 0.0
        assert data_summary["outstanding_amount"] == 0.0

    def test_outstanding_report(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="ISSUED", total_amount=100.0)
        make_payment(db, invoice_id=invoice.id, amount=10.0)

        res = client.get("/payments/outstanding", headers=admin_headers)
        assert res.status_code == 200
        
        # Look for our invoice in the report
        found = False
        for item in res.json():
            if item["invoice_id"] == invoice.id:
                assert item["outstanding_amount"] == 90.0
                found = True
                
        assert found

    def test_outstanding_report_fully_paid(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order = make_order(db, customer_id=customer.id)
        invoice = make_invoice(db, order_id=order.id, customer_id=customer.id, status="PAID", total_amount=100.0)
        make_payment(db, invoice_id=invoice.id, amount=100.0)

        res = client.get("/payments/outstanding", headers=admin_headers)
        assert res.status_code == 200
        
        # Look for our invoice in the report, it shouldn't be there
        for item in res.json():
            assert item["invoice_id"] != invoice.id

    def test_aging_report(self, client, admin_headers, db):
        from tests.factories.models import make_customer, make_order, make_invoice, make_payment
        customer = make_customer(db)
        order1 = make_order(db, customer_id=customer.id)
        order2 = make_order(db, customer_id=customer.id)
        order3 = make_order(db, customer_id=customer.id)
        order4 = make_order(db, customer_id=customer.id)
        order5 = make_order(db, customer_id=customer.id)
        order6 = make_order(db, customer_id=customer.id)
        
        now = datetime.utcnow()
        
        # CURRENT
        invoice_current = make_invoice(db, order_id=order1.id, customer_id=customer.id, status="ISSUED", total_amount=100.0, due_days=10)
        
        # 0-30 DAYS
        invoice_30 = make_invoice(db, order_id=order2.id, customer_id=customer.id, status="ISSUED", total_amount=200.0, due_days=-15)
        
        # 31-60 DAYS
        invoice_60 = make_invoice(db, order_id=order3.id, customer_id=customer.id, status="ISSUED", total_amount=300.0, due_days=-45)
        
        # 61-90 DAYS
        invoice_90 = make_invoice(db, order_id=order4.id, customer_id=customer.id, status="ISSUED", total_amount=400.0, due_days=-75)
        
        # 90+ DAYS
        invoice_old = make_invoice(db, order_id=order5.id, customer_id=customer.id, status="ISSUED", total_amount=500.0, due_days=-120)
        
        # Fully Paid
        invoice_paid = make_invoice(db, order_id=order6.id, customer_id=customer.id, status="PAID", total_amount=1000.0, due_days=-10)
        make_payment(db, invoice_id=invoice_paid.id, amount=1000.0)

        res = client.get("/payments/aging-report", headers=admin_headers)
        assert res.status_code == 200
        
        summary = res.json()["summary"]
        
        # They could have other things in the DB from other tests, so we use >=
        assert summary["current"] >= 100.0
        assert summary["0_30_days"] >= 200.0
        assert summary["31_60_days"] >= 300.0
        assert summary["61_90_days"] >= 400.0
        assert summary["90_plus_days"] >= 500.0
        
        invoices = res.json()["invoices"]
        
        for inv in invoices:
            if inv["invoice_id"] == invoice_current.id:
                assert inv["bucket"] == "CURRENT"
            elif inv["invoice_id"] == invoice_30.id:
                assert inv["bucket"] == "0-30 DAYS"
            elif inv["invoice_id"] == invoice_60.id:
                assert inv["bucket"] == "31-60 DAYS"
            elif inv["invoice_id"] == invoice_90.id:
                assert inv["bucket"] == "61-90 DAYS"
            elif inv["invoice_id"] == invoice_old.id:
                assert inv["bucket"] == "90+ DAYS"
            elif inv["invoice_id"] == invoice_paid.id:
                pytest.fail("Paid invoice should not be in aging report")
