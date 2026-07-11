"""
Unit tests for BOMService and BOM routes.
"""

import pytest
from unittest.mock import patch
from app.models.bom import BOM
from app.models.bom_item import BOMItem


@pytest.mark.unit
class TestBOMService:

    def test_create_bom_success(self, client, admin_headers, db):
        from tests.factories.models import make_product, make_raw_material, make_finished_good
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        payload = {
            "product_id": parent.id,
            "version": 1,
            "is_active": True,
            "notes": "Initial version",
            "items": [
                {
                    "component_product_id": component.id,
                    "quantity": 2.5,
                    "unit_of_measure": "KG"
                }
            ]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == parent.id
        assert data["is_active"] is True
        assert len(data["items"]) == 1
        assert data["items"][0]["component_product_id"] == component.id

    def test_create_bom_invalid_parent_type(self, client, admin_headers, db):
        from tests.factories.models import make_raw_material
        parent = make_raw_material(db)  # Parent cannot be RAW_MATERIAL
        component = make_raw_material(db)
        
        payload = {
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "must be FINISHED_GOOD or SEMI_FINISHED" in response.json()["detail"]

    def test_create_bom_parent_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_raw_material
        component = make_raw_material(db)
        
        payload = {
            "product_id": 9999,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "Parent product 9999 not found" in response.json()["detail"]

    def test_create_bom_duplicate_components(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        payload = {
            "product_id": parent.id,
            "items": [
                {"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"},
                {"component_product_id": component.id, "quantity": 2, "unit_of_measure": "PCS"}
            ]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "Duplicate component" in response.json()["detail"]

    def test_create_bom_self_reference(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good
        parent = make_finished_good(db)
        
        payload = {
            "product_id": parent.id,
            "items": [{"component_product_id": parent.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "self-reference" in response.json()["detail"]

    def test_create_bom_component_not_found(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good
        parent = make_finished_good(db)
        
        payload = {
            "product_id": parent.id,
            "items": [{"component_product_id": 9999, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 404
        assert "Component product 9999 not found" in response.json()["detail"]

    def test_create_bom_invalid_component_type(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good
        parent = make_finished_good(db)
        component = make_finished_good(db)  # Cannot be FINISHED_GOOD
        
        payload = {
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        response = client.post("/boms", json=payload, headers=admin_headers)
        assert response.status_code == 400
        assert "must be RAW_MATERIAL, SEMI_FINISHED, or PACKAGING" in response.json()["detail"]

    def test_create_bom_deactivates_older_active_bom(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        payload1 = {
            "product_id": parent.id,
            "version": 1,
            "is_active": True,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        res1 = client.post("/boms", json=payload1, headers=admin_headers)
        bom1_id = res1.json()["id"]
        
        payload2 = {
            "product_id": parent.id,
            "version": 2,
            "is_active": True,
            "items": [{"component_product_id": component.id, "quantity": 2, "unit_of_measure": "PCS"}]
        }
        res2 = client.post("/boms", json=payload2, headers=admin_headers)
        bom2_id = res2.json()["id"]
        
        # Verify bom1 is deactivated
        bom1 = db.query(BOM).filter(BOM.id == bom1_id).first()
        assert bom1.is_active is False
        
        # Verify bom2 is active
        bom2 = db.query(BOM).filter(BOM.id == bom2_id).first()
        assert bom2.is_active is True

    @patch("sqlalchemy.orm.Session.commit")
    def test_create_bom_exception(self, mock_commit, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        payload = {
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }
        
        mock_commit.side_effect = ValueError("Mock DB error")
        
        with pytest.raises(ValueError):
            client.post("/boms", json=payload, headers=admin_headers)

    def test_list_boms(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        client.post("/boms", json={
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        
        response = client.get("/boms", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_active_bom_by_product_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        client.post("/boms", json={
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        
        response = client.get(f"/boms/product/{parent.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["product_id"] == parent.id

    def test_get_active_bom_by_product_not_found(self, client, admin_headers):
        response = client.get("/boms/product/9999", headers=admin_headers)
        assert response.status_code == 404
        assert "No active BOM found" in response.json()["detail"]

    def test_get_bom_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        resp = client.post("/boms", json={
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom_id = resp.json()["id"]
        
        response = client.get(f"/boms/{bom_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["id"] == bom_id

    def test_get_bom_not_found(self, client, admin_headers):
        response = client.get("/boms/9999", headers=admin_headers)
        assert response.status_code == 404
        assert "BOM not found" in response.json()["detail"]

    def test_update_bom_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component1 = make_raw_material(db)
        component2 = make_raw_material(db)
        
        resp = client.post("/boms", json={
            "product_id": parent.id,
            "version": 1,
            "items": [{"component_product_id": component1.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom_id = resp.json()["id"]
        
        payload = {
            "version": 2,
            "notes": "Updated notes",
            "items": [
                {"component_product_id": component2.id, "quantity": 5, "unit_of_measure": "KG"}
            ]
        }
        
        response = client.put(f"/boms/{bom_id}", json=payload, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2
        assert data["notes"] == "Updated notes"
        assert len(data["items"]) == 1
        assert data["items"][0]["component_product_id"] == component2.id
        assert data["items"][0]["quantity"] == 5

    def test_update_bom_deactivates_older(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        res1 = client.post("/boms", json={
            "product_id": parent.id,
            "version": 1,
            "is_active": True,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom1_id = res1.json()["id"]
        
        res2 = client.post("/boms", json={
            "product_id": parent.id,
            "version": 2,
            "is_active": False,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom2_id = res2.json()["id"]
        
        # Now update bom2 to be active, it should deactivate bom1
        response = client.put(f"/boms/{bom2_id}", json={"is_active": True}, headers=admin_headers)
        assert response.status_code == 200
        
        bom1 = db.query(BOM).filter(BOM.id == bom1_id).first()
        assert bom1.is_active is False
        
        bom2 = db.query(BOM).filter(BOM.id == bom2_id).first()
        assert bom2.is_active is True

    def test_update_bom_not_found(self, client, admin_headers):
        response = client.put("/boms/9999", json={"version": 2}, headers=admin_headers)
        assert response.status_code == 404
        assert "BOM not found" in response.json()["detail"]

    @patch("sqlalchemy.orm.Session.commit")
    def test_update_bom_exception(self, mock_commit, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        resp = client.post("/boms", json={
            "product_id": parent.id,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom_id = resp.json()["id"]
        
        mock_commit.side_effect = ValueError("Mock DB error")
        
        with pytest.raises(ValueError):
            client.put(f"/boms/{bom_id}", json={"version": 2}, headers=admin_headers)

    def test_activate_bom_success(self, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        res1 = client.post("/boms", json={
            "product_id": parent.id,
            "is_active": True,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom1_id = res1.json()["id"]
        
        res2 = client.post("/boms", json={
            "product_id": parent.id,
            "is_active": False,
            "items": [{"component_product_id": component.id, "quantity": 2, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom2_id = res2.json()["id"]
        
        response = client.patch(f"/boms/{bom2_id}/activate", headers=admin_headers)
        assert response.status_code == 200
        
        bom1 = db.query(BOM).filter(BOM.id == bom1_id).first()
        assert bom1.is_active is False
        
        bom2 = db.query(BOM).filter(BOM.id == bom2_id).first()
        assert bom2.is_active is True

    def test_activate_bom_not_found(self, client, admin_headers):
        response = client.patch("/boms/9999/activate", headers=admin_headers)
        assert response.status_code == 404

    @patch("sqlalchemy.orm.Session.commit")
    def test_activate_bom_exception(self, mock_commit, client, admin_headers, db):
        from tests.factories.models import make_finished_good, make_raw_material
        parent = make_finished_good(db)
        component = make_raw_material(db)
        
        resp = client.post("/boms", json={
            "product_id": parent.id,
            "is_active": False,
            "items": [{"component_product_id": component.id, "quantity": 1, "unit_of_measure": "PCS"}]
        }, headers=admin_headers)
        bom_id = resp.json()["id"]
        
        mock_commit.side_effect = ValueError("Mock DB error")
        
        with pytest.raises(ValueError):
            client.patch(f"/boms/{bom_id}/activate", headers=admin_headers)
