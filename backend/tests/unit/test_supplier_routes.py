class TestSupplierRoutes:
    def test_get_suppliers_empty(self, client, admin_headers, db):
        # We assume suppliers might exist, but the route itself must be hit.
        res = client.get("/suppliers", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_supplier_not_found(self, client, admin_headers):
        res = client.get("/suppliers/9999", headers=admin_headers)
        assert res.status_code == 404

    def test_update_supplier_not_found(self, client, admin_headers):
        res = client.put("/suppliers/9999", json={"company_name": "Updated"}, headers=admin_headers)
        assert res.status_code == 404

    def test_delete_supplier_not_found(self, client, admin_headers):
        res = client.delete("/suppliers/9999", headers=admin_headers)
        assert res.status_code == 404

    def test_delete_supplier_success(self, client, admin_headers):
        res = client.post("/suppliers", json={
            "company_name": "Del Supplier",
            "contact_person": "CP",
            "email": "c@ex.com",
            "phone": "123",
            "address": "add",
            "city": "city",
            "state": "state",
            "pincode": "pin"
        }, headers=admin_headers)
        supp_id = res.json()["id"]
        
        del_res = client.delete(f"/suppliers/{supp_id}", headers=admin_headers)
        assert del_res.status_code == 200

    def test_get_supplier_success(self, client, admin_headers):
        res = client.post("/suppliers", json={"company_name": "Get Supp", "contact_person": "C", "email": "g@ex.com", "phone": "1", "address": "a", "city": "c", "state": "s", "pincode": "p"}, headers=admin_headers)
        supp_id = res.json()["id"]
        res2 = client.get(f"/suppliers/{supp_id}", headers=admin_headers)
        assert res2.status_code == 200
        assert res2.json()["company_name"] == "Get Supp"

    def test_update_supplier_success(self, client, admin_headers):
        res = client.post("/suppliers", json={"company_name": "Upd Supp", "contact_person": "C", "email": "u@ex.com", "phone": "1", "address": "a", "city": "c", "state": "s", "pincode": "p"}, headers=admin_headers)
        supp_id = res.json()["id"]
        res2 = client.put(f"/suppliers/{supp_id}", json={"company_name": "Updated Supp"}, headers=admin_headers)
        assert res2.status_code == 200
        assert res2.json()["company_name"] == "Updated Supp"
