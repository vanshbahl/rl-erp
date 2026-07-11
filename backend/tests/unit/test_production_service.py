"""
Unit tests for ProductionService.

Coverage targets:
- create_production_order: product type validation (FINISHED_GOOD / SEMI_FINISHED)
- create_production_order: active BOM required
- create_production_order: BOM snapshot scales components by quantity_planned
- create_production_order: empty BOM rejected
- check_availability: correct available/required/sufficient calculation
- execute_production: status must be IN_PROGRESS
- execute_production: duplicate execution prevention
- execute_production: inventory consumption per BOM
- execute_production: consumption_overrides applied correctly
- execute_production: insufficient stock rejected
- execute_production: finished goods added to inventory
- execute_production: PRODUCTION_CONSUMPTION and PRODUCTION_OUTPUT transactions logged
- rollback_execution: raw materials restored
- rollback_execution: finished goods removed
- rollback_execution: REVERSAL transactions logged
- rollback_execution: rejected if produced inventory already consumed
- transition_status: full state machine
"""

import pytest

pytestmark = pytest.mark.unit
