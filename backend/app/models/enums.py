from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    staff = "staff"
    viewer = "viewer"