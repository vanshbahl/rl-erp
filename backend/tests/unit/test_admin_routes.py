class TestAdminRoutes:
    def test_update_user_role_not_found(self, client, admin_headers):
        res = client.put("/admin/users/9999/role?role=manager", headers=admin_headers)
        assert res.status_code == 404
        assert res.json()["detail"] == "User not found"

    def test_get_all_users(self, client, admin_headers):
        res = client.get("/admin/users", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_user_success(self, client, admin_headers, staff_headers):
        me_res = client.get("/users/me", headers=staff_headers)
        staff_id = me_res.json()["id"]
        res = client.get(f"/admin/users/{staff_id}", headers=admin_headers)
        assert res.status_code == 200

    def test_get_user_not_found(self, client, admin_headers):
        res = client.get("/admin/users/9999", headers=admin_headers)
        assert res.status_code == 404

    def test_delete_user_not_found(self, client, admin_headers):
        res = client.delete("/admin/users/9999", headers=admin_headers)
        assert res.status_code == 404

    def test_delete_own_account(self, client, admin_headers):
        me_res = client.get("/users/me", headers=admin_headers)
        my_id = me_res.json()["id"]
        res = client.delete(f"/admin/users/{my_id}", headers=admin_headers)
        assert res.status_code == 400
        assert "cannot delete your own account" in res.json()["detail"].lower()
        
    def test_delete_user_success(self, client, admin_headers, db):
        # Create a temporary user to delete
        from app.models.user import User
        from app.core.security import hash_password
        new_user = User(username="del_user", email="del@ex.com", hashed_password=hash_password("pw"))
        db.add(new_user)
        db.commit()
        
        res = client.delete(f"/admin/users/{new_user.id}", headers=admin_headers)
        assert res.status_code == 200

    def test_update_user_role_success(self, client, admin_headers, staff_headers):
        me_res = client.get("/users/me", headers=staff_headers)
        staff_id = me_res.json()["id"]
        res = client.put(f"/admin/users/{staff_id}/role?role=manager", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["role"] == "manager"
