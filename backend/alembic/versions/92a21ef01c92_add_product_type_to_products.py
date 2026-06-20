"""add product_type to products

Revision ID: 92a21ef01c92
Revises: 686fc3352513
Create Date: 2026-06-20 23:46:25.261328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92a21ef01c92'
down_revision: Union[str, Sequence[str], None] = '686fc3352513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add nullable column
    op.add_column('products', sa.Column('product_type', sa.String(), nullable=True))
    
    # 2. Backfill existing rows to 'FINISHED_GOOD'
    op.execute("UPDATE products SET product_type = 'FINISHED_GOOD' WHERE product_type IS NULL")
    
    # 3. Make column non-nullable
    op.alter_column('products', 'product_type', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('products', 'product_type')
