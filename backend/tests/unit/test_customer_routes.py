class TestCustomerRoutes:
    def test_get_customer_not_found(self, client, admin_headers):
        res = client.get("/customers/9999", headers=admin_headers)
        assert res.status_code == 404

    def test_update_customer_not_found(self, client, admin_headers):
        res = client.put("/customers/9999", json={"company_name": "Updated", "email": "test@ex.com"}, headers=admin_headers)
        assert res.status_code == 404

    def test_deactivate_customer_not_found(self, client, admin_headers):
        res = client.patch("/customers/9999/deactivate", headers=admin_headers)
        assert res.status_code == 404
        
    def test_deactivate_customer_success(self, client, admin_headers):
        res = client.post("/customers/", json={"company_name": "To Deactivate", "email": "deact@ex.com", "phone": "123", "address": "add", "city": "city", "state": "state", "pincode": "pin"}, headers=admin_headers)
        cust_id = res.json()["id"]
        
        del_res = client.patch(f"/customers/{cust_id}/deactivate", headers=admin_headers)
        assert del_res.status_code == 200

    def test_get_customer_success(self, client, admin_headers):
        res = client.post("/customers/", json={"company_name": "Get Cust", "email": "get@ex.com"}, headers=admin_headers)
        cust_id = res.json()["id"]
        res2 = client.get(f"/customers/{cust_id}", headers=admin_headers)
        assert res2.status_code == 200
        assert res2.json()["company_name"] == "Get Cust"

    def test_update_customer_success(self, client, admin_headers):
        res = client.post("/customers/", json={"company_name": "Upd Cust", "email": "upd@ex.com"}, headers=admin_headers)
        cust_id = res.json()["id"]
        res2 = client.put(f"/customers/{cust_id}", json={"company_name": "Updated Cust"}, headers=admin_headers)
        assert res2.status_code == 200
        assert res2.json()["company_name"] == "Updated Cust"
