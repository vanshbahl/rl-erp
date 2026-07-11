"""
Unit tests for InvoiceService.

Coverage targets:
- generate_invoice: order status guard (must be DISPATCHED or COMPLETED)
- generate_invoice: duplicate invoice prevention (one per order)
- generate_invoice: invoice number sequential format (INV-000001)
- generate_invoice: due_days validation (must be > 0)
- generate_invoice: invoice items copied from order items
- transition_status: full state machine
  (DRAFT→ISSUED→PARTIALLY_PAID→PAID, each CANCELLED path)
- transition_status: backwards transitions rejected
"""

import pytest

pytestmark = pytest.mark.unit
