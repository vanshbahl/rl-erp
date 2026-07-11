"""
Unit tests for BOMService.

Coverage targets:
- create_bom: product type validation (must be FINISHED_GOOD or SEMI_FINISHED)
- create_bom: self-reference prevention
- create_bom: duplicate component prevention within one BOM
- create_bom: deactivates existing active BOM for same product
- update_bom: version increment on component change
- activate_bom: deactivates previously active BOM
- get_active_bom_by_product: returns correct active BOM
"""

import pytest

pytestmark = pytest.mark.unit
