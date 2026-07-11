class TestUserRoutes:
    def test_get_me(self, client, admin_headers):
        res = client.get("/users/me", headers=admin_headers)
        assert res.status_code == 200
        assert "username" in res.json()
        assert "email" in res.json()
        assert "id" in res.json()
