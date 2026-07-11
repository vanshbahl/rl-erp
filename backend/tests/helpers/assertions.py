"""
Assertion helpers — reusable checks for common ERP business invariants.

Each helper takes concrete values, not response dicts, to keep test
bodies readable and assertion messages precise.
"""

from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.invoice import Invoice


def assert_inventory_quantity(db: Session, product_id: int, expected: float):
    """Assert that a product's current inventory equals the expected quantity."""
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    assert inv is not None, f"No inventory record for product {product_id}"
    assert float(inv.quantity) == pytest_approx(expected), (
        f"Inventory for product {product_id}: expected {expected}, got {inv.quantity}"
    )


def assert_invoice_status(db: Session, invoice_id: int, expected_status: str):
    """Assert that an invoice is in the expected status."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    assert inv is not None, f"Invoice {invoice_id} not found"
    assert inv.status == expected_status, (
        f"Invoice {invoice_id}: expected status {expected_status!r}, got {inv.status!r}"
    )


def assert_response_error(response_json: dict, expected_fragment: str):
    """Assert that an error response body contains an expected substring."""
    detail = response_json.get("detail", "")
    assert expected_fragment.lower() in str(detail).lower(), (
        f"Expected error containing {expected_fragment!r}, got: {detail!r}"
    )


try:
    from pytest import approx as pytest_approx
except ImportError:
    def pytest_approx(x):
        return x
