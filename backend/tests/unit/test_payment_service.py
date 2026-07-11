"""
Unit tests for PaymentService.

Coverage targets:
- create_payment: invoice validation (must exist and be ISSUED/PARTIALLY_PAID)
- create_payment: overpayment prevention (amount > outstanding balance)
- create_payment: invoice moves to PARTIALLY_PAID on partial payment
- create_payment: invoice moves to PAID when balance cleared
- invoice_summary: outstanding balance calculation
- outstanding_report: lists invoices with balance > 0
- aging_report: correct aging bucket classification
"""

import pytest

pytestmark = pytest.mark.unit
