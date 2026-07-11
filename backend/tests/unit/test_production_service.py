"""
Unit tests for ProductionService and routes.
"""

import pytest
from unittest.mock import patch
from app.models.production_order import ProductionOrder
from app.models.production_execution import ProductionExecution
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.bom import BOM
from app.models.bom_item import BOMItem


@pytest.mark.unit
class TestProductionService:

    def _setup_bom_with_items(self, db, parent_id, component_id, quantity=2, is_active=True):
        from tests.factories.models import make_bom, make_bom_item
        bom = make_bom(db, product_id=parent_id, is_active=is_active)
        make_bom_item(db, bom_id=bom.id, component_product_id=component_id, quantity=quantity)
        return bom

    def test_create_production_order_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        self._setup_bom_with_items(db, parent.id, component.id)
        
        payload = {
            "product_id": parent.id,
            "quantity_planned": 10.0,
            "notes": "Test order"
        }
        
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == parent.id
        assert data["quantity_planned"] == 10.0
        assert data["status"] == "DRAFT"
        assert len(data["items"]) == 1
        assert data["items"][0]["component_product_id"] == component.id
        assert data["items"][0]["quantity_required"] == 20.0

    def test_create_order_product_not_found(self, client, admin_headers):
        payload = {"product_id": 9999, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_order_invalid_product_type(self, client, admin_headers, db):
        from tests.factories.models import make_raw_material
        product = make_raw_material(db)
        
        payload = {"product_id": product.id, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "must be FINISHED_GOOD" in response.json()["detail"]

    def test_create_order_no_active_bom(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        self._setup_bom_with_items(db, parent.id, component.id, is_active=False)
        
        payload = {"product_id": parent.id, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "No active BOM" in response.json()["detail"]

    def test_create_order_bom_no_items(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_bom
        parent = make_finished_good(db)
        
        make_bom(db, product_id=parent.id, is_active=True)
        
        payload = {"product_id": parent.id, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "does not contain any component items" in response.json()["detail"]

    def test_create_order_bom_self_reference(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good
        parent = make_finished_good(db)
        
        self._setup_bom_with_items(db, parent.id, parent.id)
        
        payload = {"product_id": parent.id, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "self-reference" in response.json()["detail"]



    def test_create_order_bom_invalid_component_type(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good
        parent = make_finished_good(db)
        component = make_finished_good(db)  # Invalid component type
        
        self._setup_bom_with_items(db, parent.id, component.id)
        
        payload = {"product_id": parent.id, "quantity_planned": 10.0}
        response = client.post("/production-orders", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "RAW_MATERIAL, SEMI_FINISHED, or PACKAGING" in response.json()["detail"]

    def test_create_order_exception(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        self._setup_bom_with_items(db, parent.id, component.id)
        
        payload = {"product_id": parent.id, "quantity_planned": 10.0}
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.post("/production-orders", json=payload, headers=admin_headers)

    def test_list_and_get_orders(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        
        list_res = client.get("/production-orders", headers=admin_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        
        get_res = client.get(f"/production-orders/{order_id}", headers=admin_headers)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == order_id
        
        get_fail = client.get("/production-orders/9999", headers=admin_headers)
        assert get_fail.status_code == 404

    def test_transition_status(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        
        # DRAFT -> PLANNED
        patch_res = client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "PLANNED"
        
        # PLANNED -> IN_PROGRESS
        patch_res2 = client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        assert patch_res2.status_code == 200
        assert patch_res2.json()["status"] == "IN_PROGRESS"

        # IN_PROGRESS -> PLANNED (Invalid)
        patch_res3 = client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        assert patch_res3.status_code == 400
        assert "not allowed" in patch_res3.json()["detail"]

    def test_transition_status_completed_or_cancelled_errors(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        # Test Cancelled
        res1 = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id_1 = res1.json()["id"]
        
        client.patch(f"/production-orders/{order_id_1}/status", json={"status": "CANCELLED"}, headers=admin_headers)
        patch_cancelled = client.patch(f"/production-orders/{order_id_1}/status", json={"status": "PLANNED"}, headers=admin_headers)
        assert patch_cancelled.status_code == 400
        assert "terminal" in patch_cancelled.json()["detail"]

        # Test Completed
        res2 = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id_2 = res2.json()["id"]
        order = db.query(ProductionOrder).get(order_id_2)
        order.status = "COMPLETED"
        db.commit()
        
        patch_completed = client.patch(f"/production-orders/{order_id_2}/status", json={"status": "PLANNED"}, headers=admin_headers)
        assert patch_completed.status_code == 400
        assert "completed" in patch_completed.json()["detail"].lower()

    def test_transition_status_exception(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)

    def test_check_availability(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id, quantity=2)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 5}, headers=admin_headers)
        order_id = res.json()["id"]
        
        avail_res = client.get(f"/production-orders/{order_id}/availability", headers=admin_headers)
        assert avail_res.status_code == 200
        data = avail_res.json()
        assert len(data) == 1
        assert data[0]["component_product_id"] == component.id
        assert data[0]["quantity_required"] == 10.0
        assert data[0]["quantity_available"] == 0.0
        assert data[0]["is_sufficient"] is False

    def test_execute_production_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id, quantity=2)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        exec_payload = {
            "quantity_produced": 10,
            "notes": "Finished batch"
        }
        exec_res = client.post(f"/production-orders/{order_id}/execute", json=exec_payload, headers=admin_headers)
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        assert exec_data["status"] == "COMPLETED"
        
        comp_inv = db.query(Inventory).filter(Inventory.product_id == component.id).first()
        assert comp_inv.quantity == 80.0
        
        fg_inv = db.query(Inventory).filter(Inventory.product_id == parent.id).first()
        assert fg_inv is not None
        assert fg_inv.quantity == 10.0
        
        execs_res = client.get(f"/production-orders/{order_id}/executions", headers=admin_headers)
        assert len(execs_res.json()) == 1

    def test_execute_production_not_in_progress(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        
        exec_res = client.post(f"/production-orders/{order_id}/execute", json={}, headers=admin_headers)
        assert exec_res.status_code == 400
        assert "IN_PROGRESS" in exec_res.json()["detail"]

    def test_execute_production_insufficient_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        exec_res = client.post(f"/production-orders/{order_id}/execute", json={}, headers=admin_headers)
        assert exec_res.status_code == 400
        assert "Insufficient inventory" in exec_res.json()["detail"]

    def test_execute_production_already_completed(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        client.post(f"/production-orders/{order_id}/execute", json={}, headers=admin_headers)
        
        order = db.query(ProductionOrder).get(order_id)
        order.status = "IN_PROGRESS"
        db.commit()
        
        exec_res = client.post(f"/production-orders/{order_id}/execute", json={}, headers=admin_headers)
        assert exec_res.status_code == 400
        assert "completed execution already exists" in exec_res.json()["detail"]

    def test_execute_production_exception(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.post(f"/production-orders/{order_id}/execute", json={"quantity_produced": 10}, headers=admin_headers)

    def test_rollback_execution_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id, quantity=2)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        client.post(f"/production-orders/{order_id}/execute", json={"quantity_produced": 10}, headers=admin_headers)
        
        roll_res = client.post(f"/production-orders/{order_id}/rollback", headers=admin_headers)
        assert roll_res.status_code == 200
        assert roll_res.json()["status"] == "ROLLED_BACK"
        
        order = db.query(ProductionOrder).get(order_id)
        assert order.status == "IN_PROGRESS"
        
        comp_inv = db.query(Inventory).filter(Inventory.product_id == component.id).first()
        assert comp_inv.quantity == 100.0
        
        fg_inv = db.query(Inventory).filter(Inventory.product_id == parent.id).first()
        assert fg_inv.quantity == 0.0

    def test_rollback_execution_no_completed(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        
        roll_res = client.post(f"/production-orders/{order_id}/rollback", headers=admin_headers)
        assert roll_res.status_code == 400
        assert "No completed execution found" in roll_res.json()["detail"]

    def test_rollback_execution_inventory_consumed(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        client.post(f"/production-orders/{order_id}/execute", json={"quantity_produced": 10}, headers=admin_headers)
        
        fg_inv = db.query(Inventory).filter(Inventory.product_id == parent.id).first()
        fg_inv.quantity = 5.0
        db.commit()
        
        roll_res = client.post(f"/production-orders/{order_id}/rollback", headers=admin_headers)
        assert roll_res.status_code == 400
        assert "has already been consumed" in roll_res.json()["detail"]

    def test_rollback_missing_component_inventory(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id, quantity=2)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        client.post(f"/production-orders/{order_id}/execute", json={"quantity_produced": 10}, headers=admin_headers)
        
        db.query(Inventory).filter(Inventory.product_id == component.id).delete()
        db.commit()
        
        roll_res = client.post(f"/production-orders/{order_id}/rollback", headers=admin_headers)
        assert roll_res.status_code == 200
        
        new_inv = db.query(Inventory).filter(Inventory.product_id == component.id).first()
        assert new_inv is not None
        assert new_inv.quantity == 20.0

    def test_rollback_execution_exception(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        client.post(f"/production-orders/{order_id}/execute", json={"quantity_produced": 10}, headers=admin_headers)
        
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = ValueError("Mock Exception")
            with pytest.raises(ValueError):
                client.post(f"/production-orders/{order_id}/rollback", headers=admin_headers)

    def test_execute_with_consumption_overrides(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material, make_inventory
        parent = make_finished_good(db)
        component = make_raw_material(db)
        self._setup_bom_with_items(db, parent.id, component.id, quantity=2)
        make_inventory(db, product_id=component.id, quantity=100.0)
        
        res = client.post("/production-orders", json={"product_id": parent.id, "quantity_planned": 10}, headers=admin_headers)
        order_id = res.json()["id"]
        client.patch(f"/production-orders/{order_id}/status", json={"status": "PLANNED"}, headers=admin_headers)
        client.patch(f"/production-orders/{order_id}/status", json={"status": "IN_PROGRESS"}, headers=admin_headers)
        
        exec_payload = {
            "quantity_produced": 10,
            "consumption_overrides": [
                {
                    "component_product_id": component.id,
                    "quantity_consumed": 25.0
                }
            ]
        }
        
        exec_res = client.post(f"/production-orders/{order_id}/execute", json=exec_payload, headers=admin_headers)
        assert exec_res.status_code == 200
        
        comp_inv = db.query(Inventory).filter(Inventory.product_id == component.id).first()
        assert comp_inv.quantity == 75.0
