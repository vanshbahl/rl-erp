"""
HTTP helper utilities for tests.

Provides thin wrappers around the TestClient that:
- Inject auth headers automatically
- Assert expected status codes and return parsed JSON
- Give clean failure messages on unexpected status
"""

from typing import Any


def post(client, url: str, json: dict, headers: dict, expected_status: int = 200) -> Any:
    response = client.post(url, json=json, headers=headers)
    assert response.status_code == expected_status, (
        f"POST {url} expected {expected_status}, got {response.status_code}: {response.text}"
    )
    return response.json()


def get(client, url: str, headers: dict, expected_status: int = 200) -> Any:
    response = client.get(url, headers=headers)
    assert response.status_code == expected_status, (
        f"GET {url} expected {expected_status}, got {response.status_code}: {response.text}"
    )
    return response.json()


def patch(client, url: str, json: dict, headers: dict, expected_status: int = 200) -> Any:
    response = client.patch(url, json=json, headers=headers)
    assert response.status_code == expected_status, (
        f"PATCH {url} expected {expected_status}, got {response.status_code}: {response.text}"
    )
    return response.json()


def put(client, url: str, json: dict, headers: dict, expected_status: int = 200) -> Any:
    response = client.put(url, json=json, headers=headers)
    assert response.status_code == expected_status, (
        f"PUT {url} expected {expected_status}, got {response.status_code}: {response.text}"
    )
    return response.json()
