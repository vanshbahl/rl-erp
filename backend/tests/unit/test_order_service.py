"""
Unit tests for OrderService.

Coverage targets:
- create_order: customer validation, item validation, total calculation
- transition_status: every valid transition
- transition_status: every invalid/backward/skipped transition (state machine)
- _dispatch_order: inventory deduction, transaction logging
- _dispatch_order: insufficient stock rejection
- _cancel_order: inventory restoration from DISPATCHED only
- Double dispatch prevention
"""

import pytest

pytestmark = pytest.mark.unit
