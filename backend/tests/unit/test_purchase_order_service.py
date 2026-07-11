"""
Unit tests for PurchaseOrderService.

Coverage targets:
- create_purchase_order: supplier validation, item validation, total calculation
- create_purchase_order: PO number uniqueness (no duplicates)
- transition_status: full state machine (DRAFT→SENT→PARTIALLY_RECEIVED→RECEIVED→CANCELLED)
- receive_goods: inventory increment, transaction log creation
- receive_goods: over-receiving prevention
- receive_goods: PARTIALLY_RECEIVED → RECEIVED auto-transition when all items received
"""

import pytest

pytestmark = pytest.mark.unit
