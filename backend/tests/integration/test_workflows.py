"""
Integration tests for RL-ERP business workflows.
"""

import pytest

@pytest.mark.integration
class TestBusinessWorkflows:
    def test_workflow_1_product_to_inventory(self, client, admin_headers, db):
        """
        Workflow 1: Product -> Inventory
        Verifies that creating a product automatically creates a default inventory record.
        """
        # 1. Create Product
        product_payload = {
            "sku": "INT-PROD-001",
            "name": "Integration Test Product",
            "description": "A product for integration testing",
            "category": "Raw Materials",
            "price": 10.50,
            "product_type": "RAW_MATERIAL"
        }
        res_prod = client.post("/products", json=product_payload, headers=admin_headers)
        assert res_prod.status_code == 200
        product_data = res_prod.json()
        product_id = product_data["id"]

        # 2. Verify Inventory
        res_inv = client.get(f"/inventory/{product_id}", headers=admin_headers)
        assert res_inv.status_code == 200
        inventory_data = res_inv.json()
        assert inventory_data["product_id"] == product_id
        assert inventory_data["quantity"] == 0.0

    def test_workflow_2_customer_order_dispatch_inventory(self, client, admin_headers, db):
        """
        Workflow 2: Customer -> Order -> Dispatch -> Inventory Reduced
        """
        # 1. Create Product and set stock
        prod_res = client.post("/products", json={"sku": "INT-PROD-002", "name": "Finished Good", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]
        
        client.put(f"/inventory/{product_id}", json={"quantity": 50.0}, headers=admin_headers)

        # 2. Create Customer
        cust_res = client.post("/customers", json={"company_name": "Test Customer", "email": "test@example.com"}, headers=admin_headers)
        customer_id = cust_res.json()["id"]

        # 3. Create Order
        order_payload = {
            "customer_id": customer_id,
            "contact_person": "Test Contact",
            "items": [
                {"product_id": product_id, "quantity": 10.0, "rate": 100.0}
            ]
        }
        order_res = client.post("/orders", json=order_payload, headers=admin_headers)
        assert order_res.status_code == 200
        order_id = order_res.json()["order_id"]

        # Verify inventory NOT reduced yet
        inv_before = client.get(f"/inventory/{product_id}", headers=admin_headers).json()
        assert inv_before["quantity"] == 50.0

        # 4. Dispatch Order
        process_res = client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        assert process_res.status_code == 200
        dispatch_res = client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        assert dispatch_res.status_code == 200

        # 5. Verify Inventory Reduced
        inv_after = client.get(f"/inventory/{product_id}", headers=admin_headers).json()
        assert inv_after["quantity"] == 40.0

    def test_workflow_3_dispatch_invoice_payment(self, client, admin_headers, db):
        """
        Workflow 3: Dispatch -> Invoice -> Payment -> Invoice Paid
        """
        # Create dependencies
        prod_res = client.post("/products", json={"sku": "INT-PROD-003", "name": "Item 3", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]
        client.put(f"/inventory/{product_id}", json={"quantity": 50.0}, headers=admin_headers)
        
        cust_res = client.post("/customers", json={"company_name": "Payer Customer", "email": "payer@example.com"}, headers=admin_headers)
        customer_id = cust_res.json()["id"]

        order_res = client.post("/orders", json={"customer_id": customer_id, "contact_person": "Payer Contact", "items": [{"product_id": product_id, "quantity": 5.0, "rate": 100.0}]}, headers=admin_headers)
        order_id = order_res.json()["order_id"]
        
        # 1. Dispatch Order
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        
        # 2. Generate Invoice
        inv_gen_res = client.post(f"/invoices/generate/{order_id}?due_days=30", headers=admin_headers)
        assert inv_gen_res.status_code == 200
        invoice_id = inv_gen_res.json()["invoice_id"]
        # Invoices return "invoice_id" instead of "id", but "total_amount" is only available on getting the invoice.
        inv_get_initial = client.get(f"/invoices/{invoice_id}", headers=admin_headers).json()["invoice"]
        assert inv_get_initial["status"] == "DRAFT"
        assert inv_get_initial["total_amount"] == 500.0

        # 3. Issue Invoice
        client.patch(f"/invoices/{invoice_id}/status", json={"status": "ISSUED"}, headers=admin_headers)

        # 4. Partial Payment
        pay1_res = client.post("/payments", json={"invoice_id": invoice_id, "amount": 200.0, "payment_method": "BANK_TRANSFER"}, headers=admin_headers)
        assert pay1_res.status_code == 200
        
        # Verify invoice is partially paid
        inv_get = client.get(f"/invoices/{invoice_id}", headers=admin_headers).json()["invoice"]
        assert inv_get["status"] == "PARTIALLY_PAID"

        # 4. Final Payment
        pay2_res = client.post("/payments", json={"invoice_id": invoice_id, "amount": 300.0, "payment_method": "BANK_TRANSFER"}, headers=admin_headers)
        assert pay2_res.status_code == 200
        
        # 5. Verify Invoice Paid
        inv_get2 = client.get(f"/invoices/{invoice_id}", headers=admin_headers).json()["invoice"]
        assert inv_get2["status"] == "PAID"

    def test_workflow_4_purchase_order_receive_inventory(self, client, admin_headers, db):
        """
        Workflow 4: Purchase Order -> Receive -> Inventory Increased
        """
        # Create supplier & product
        sup_res = client.post("/suppliers", json={"company_name": "Supplier A", "email": "sup@example.com"}, headers=admin_headers)
        supplier_id = sup_res.json()["id"]
        
        prod_res = client.post("/products", json={"sku": "INT-PROD-004", "name": "Raw Material 4", "product_type": "RAW_MATERIAL", "price": 50.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]

        inv_before = client.get(f"/inventory/{product_id}", headers=admin_headers).json()
        assert inv_before["quantity"] == 0.0

        # 1. Purchase Order
        po_payload = {
            "supplier_id": supplier_id,
            "items": [
                {"product_id": product_id, "quantity": 100.0, "rate": 45.0}
            ]
        }
        po_res = client.post("/purchase-orders", json=po_payload, headers=admin_headers)
        assert po_res.status_code == 200
        po_id = po_res.json()["id"]
        assert po_res.json()["status"] == "DRAFT"
        
        client.patch(f"/purchase-orders/{po_id}/status", json={"status": "ISSUED"}, headers=admin_headers)

        # 2. Receive
        client.post(f"/purchase-orders/{po_id}/receive", json={"items": [{"product_id": product_id, "received_quantity": 100.0}]}, headers=admin_headers)

        # 3. Inventory Increased
        inv_after = client.get(f"/inventory/{product_id}", headers=admin_headers).json()
        assert inv_after["quantity"] == 100.0

    def test_workflow_5_bom_production_execution_finished_goods(self, client, admin_headers, db):
        """
        Workflow 5: BOM -> Production -> Execution -> Finished Goods
        """
        # Create raw materials
        rm_res = client.post("/products", json={"sku": "INT-RM-001", "name": "Raw 1", "product_type": "RAW_MATERIAL", "price": 10.0}, headers=admin_headers)
        rm_id = rm_res.json()["id"]
        client.put(f"/inventory/{rm_id}", json={"quantity": 200.0}, headers=admin_headers)
        
        # Create finished good
        fg_res = client.post("/products", json={"sku": "INT-FG-001", "name": "Fin 1", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        fg_id = fg_res.json()["id"]
        
        # 1. Create BOM
        bom_payload = {
            "product_id": fg_id,
            "version": 1,
            "is_active": True,
            "items": [
                {"component_product_id": rm_id, "quantity": 2.5, "unit_of_measure": "kg"}
            ]
        }
        bom_res = client.post("/boms", json=bom_payload, headers=admin_headers)
        assert bom_res.status_code == 200
        bom_id = bom_res.json()["id"]

        # 2. Production Order
        prod_payload = {
            "product_id": fg_id,
            "quantity_planned": 10.0
        }
        prod_res = client.post("/production-orders", json=prod_payload, headers=admin_headers)
        assert prod_res.status_code == 200
        prod_id = prod_res.json()["id"]
        
        # Move to PLANNED -> IN_PROGRESS
        client.patch(f"/production-orders/{prod_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{prod_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        # 3. Execution
        exec_payload = {
            "yield_quantity": 10.0,
            "components": [
                {"component_product_id": rm_id, "quantity_used": 25.0} # 10 * 2.5
            ]
        }
        exec_res = client.post(f"/production-orders/{prod_id}/execute", json=exec_payload, headers=admin_headers)
        assert exec_res.status_code == 200
        
        # 4. Verify Inventory (Finished goods increased, Raw Materials decreased)
        inv_rm = client.get(f"/inventory/{rm_id}", headers=admin_headers).json()
        assert inv_rm["quantity"] == 175.0 # 200 - 25
        
        inv_fg = client.get(f"/inventory/{fg_id}", headers=admin_headers).json()
        assert inv_fg["quantity"] == 10.0

    def test_workflow_6_production_rollback(self, client, admin_headers, db):
        """
        Workflow 6: Production -> Rollback -> Inventory Restored
        """
        # Create raw materials
        rm_res = client.post("/products", json={"sku": "INT-RM-002", "name": "Raw 2", "product_type": "RAW_MATERIAL", "price": 10.0}, headers=admin_headers)
        rm_id = rm_res.json()["id"]
        client.put(f"/inventory/{rm_id}", json={"quantity": 100.0}, headers=admin_headers)
        
        # Create finished good
        fg_res = client.post("/products", json={"sku": "INT-FG-002", "name": "Fin 2", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        fg_id = fg_res.json()["id"]
        
        # BOM
        client.post("/boms", json={
            "product_id": fg_id, "version": 1, "is_active": True,
            "items": [{"component_product_id": rm_id, "quantity": 5.0, "unit_of_measure": "kg"}]
        }, headers=admin_headers)
        
        # Production Order & Execution
        prod_id = client.post("/production-orders", json={"product_id": fg_id, "quantity_planned": 10.0}, headers=admin_headers).json()["id"]
        client.patch(f"/production-orders/{prod_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{prod_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        exec_id = client.post(f"/production-orders/{prod_id}/execute", json={"yield_quantity": 10.0, "components": [{"component_product_id": rm_id, "quantity_used": 50.0}]}, headers=admin_headers).json()["id"]
        
        # Verify Inventory before rollback
        assert client.get(f"/inventory/{rm_id}", headers=admin_headers).json()["quantity"] == 50.0
        assert client.get(f"/inventory/{fg_id}", headers=admin_headers).json()["quantity"] == 10.0
        
        # 1. Rollback
        roll_res = client.post(f"/production-orders/{prod_id}/rollback", json={"execution_id": exec_id}, headers=admin_headers)
        assert roll_res.status_code == 200
        
        # 2. Inventory Restored
        assert client.get(f"/inventory/{rm_id}", headers=admin_headers).json()["quantity"] == 100.0
        assert client.get(f"/inventory/{fg_id}", headers=admin_headers).json()["quantity"] == 0.0

    def test_workflow_7_invalid_dispatch(self, client, admin_headers, db):
        # 1. Order without inventory
        prod_res = client.post("/products", json={"sku": "INT-PROD-005", "name": "Out Of Stock", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]
        
        cust_res = client.post("/customers", json={"company_name": "Bad Flow Customer", "email": "bad@example.com"}, headers=admin_headers)
        customer_id = cust_res.json()["id"]

        order_res = client.post("/orders", json={"customer_id": customer_id, "contact_person": "Bad Flow Contact", "items": [{"product_id": product_id, "quantity": 10.0, "rate": 100.0}]}, headers=admin_headers)
        order_id = order_res.json()["order_id"]
        
        # Try to dispatch without inventory
        client.patch(f"/orders/{order_id}/status", json={"status": "PROCESSING"}, headers=admin_headers)
        dispatch_res = client.patch(f"/orders/{order_id}/status", json={"status": "DISPATCHED"}, headers=admin_headers)
        assert dispatch_res.status_code == 400
        assert "insufficient inventory" in dispatch_res.json()["detail"].lower()
        
    def test_workflow_7_invalid_transition(self, client, admin_headers, db):
        prod_res = client.post("/products", json={"sku": "INT-PROD-006", "name": "Trans Flow", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]
        cust_res = client.post("/customers", json={"company_name": "Trans Flow Customer", "email": "bad2@example.com"}, headers=admin_headers)
        customer_id = cust_res.json()["id"]
        order_res = client.post("/orders", json={"customer_id": customer_id, "contact_person": "Trans Flow Contact", "items": [{"product_id": product_id, "quantity": 10.0, "rate": 100.0}]}, headers=admin_headers)
        order_id = order_res.json()["order_id"]

        # 2. Invalid state transitions (Order COMPLETED directly from PENDING)
        complete_res = client.patch(f"/orders/{order_id}/status", json={"status": "COMPLETED"}, headers=admin_headers)
        assert complete_res.status_code == 400
        assert "not allowed" in complete_res.json()["detail"].lower()
        
    def test_workflow_7_invalid_payment(self, client, admin_headers, db):
        # 3. Pay for non-existent invoice
        pay_res = client.post("/payments", json={"invoice_id": 9999, "amount": 100.0, "payment_method": "CASH"}, headers=admin_headers)
        assert pay_res.status_code == 404
        
    def test_workflow_7_invalid_invoice(self, client, admin_headers, db):
        prod_res = client.post("/products", json={"sku": "INT-PROD-007", "name": "Inv Flow", "product_type": "FINISHED_GOOD", "price": 100.0}, headers=admin_headers)
        product_id = prod_res.json()["id"]
        cust_res = client.post("/customers", json={"company_name": "Inv Flow Customer", "email": "bad3@example.com"}, headers=admin_headers)
        customer_id = cust_res.json()["id"]
        order_res = client.post("/orders", json={"customer_id": customer_id, "contact_person": "Inv Flow Contact", "items": [{"product_id": product_id, "quantity": 10.0, "rate": 100.0}]}, headers=admin_headers)
        order_id = order_res.json()["order_id"]

        # 4. Generate invoice for un-dispatched order
        inv_res = client.post(f"/invoices/generate/{order_id}?due_days=30", headers=admin_headers)
        assert inv_res.status_code == 400
        assert "dispatched or completed" in inv_res.json()["detail"].lower()
