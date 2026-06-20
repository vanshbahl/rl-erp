"""create bom and bom_item tables

Revision ID: cf06b217a05b
Revises: c69c1886d559
Create Date: 2026-06-21 00:02:41.947660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf06b217a05b'
down_revision: Union[str, Sequence[str], None] = 'c69c1886d559'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create boms table
    op.create_table(
        'boms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boms_id'), 'boms', ['id'], unique=False)

    # Create bom_items table
    op.create_table(
        'bom_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bom_id', sa.Integer(), nullable=False),
        sa.Column('component_product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_of_measure', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['bom_id'], ['boms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['component_product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bom_id', 'component_product_id', name='uq_bom_items_bom_component')
    )
    op.create_index(op.f('ix_bom_items_id'), 'bom_items', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_bom_items_id'), table_name='bom_items')
    op.drop_table('bom_items')
    op.drop_index(op.f('ix_boms_id'), table_name='boms')
    op.drop_table('boms')
