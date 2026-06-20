from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


# Inventory Transaction Types
class InventoryTransactionType(str, Enum):
    SALE = "SALE"
    PURCHASE_RECEIPT = "PURCHASE_RECEIPT"
    ADJUSTMENT = "ADJUSTMENT"
    PRODUCTION_CONSUMPTION = "PRODUCTION_CONSUMPTION"
    PRODUCTION_OUTPUT = "PRODUCTION_OUTPUT"
    REVERSAL = "REVERSAL"


class ProductType(str, Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    FINISHED_GOOD = "FINISHED_GOOD"
    SEMI_FINISHED = "SEMI_FINISHED"
    PACKAGING = "PACKAGING"
    CONSUMABLE = "CONSUMABLE"