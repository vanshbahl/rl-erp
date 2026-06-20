"""add raw material fields to products

Revision ID: c69c1886d559
Revises: 92a21ef01c92
Create Date: 2026-06-20 23:53:19.866205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c69c1886d559'
down_revision: Union[str, Sequence[str], None] = '92a21ef01c92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add both columns as nullable
    op.add_column('products', sa.Column('standard_cost', sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column('products', sa.Column('default_supplier_id', sa.Integer(), nullable=True))
    
    # 2. Add foreign key constraint
    op.create_foreign_key('fk_products_default_supplier', 'products', 'suppliers', ['default_supplier_id'], ['id'])
    
    # 3. Backfill standard_cost = 0.00 for existing rows
    op.execute("UPDATE products SET standard_cost = 0.00 WHERE standard_cost IS NULL")
    
    # 4. Make standard_cost non-nullable
    op.alter_column('products', 'standard_cost', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop foreign key constraint
    op.drop_constraint('fk_products_default_supplier', 'products', type_='foreignkey')
    
    # 2. Drop columns
    op.drop_column('products', 'default_supplier_id')
    op.drop_column('products', 'standard_cost')
