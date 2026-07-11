"""add unique constraint to po_number

Revision ID: 55b4c087d613
Revises: 75dbc95f9297
Create Date: 2026-07-11 14:12:28.877835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55b4c087d613'
down_revision: Union[str, Sequence[str], None] = '75dbc95f9297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_purchase_order_number",
        "purchase_orders",
        ["po_number"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_purchase_order_number",
        "purchase_orders",
        type_="unique"
    )
