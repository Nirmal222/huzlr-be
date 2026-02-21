"""create property_preferences table

Revision ID: c1a2b3d4e5f6
Revises: b6c91ce6afb9
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b6c91ce6afb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the property_preferences table."""
    op.create_table(
        'property_preferences',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'entity_type', name='uq_user_entity_preference'),
    )
    op.create_index(op.f('ix_property_preferences_id'), 'property_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_property_preferences_user_id'), 'property_preferences', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop the property_preferences table."""
    op.drop_index(op.f('ix_property_preferences_user_id'), table_name='property_preferences')
    op.drop_index(op.f('ix_property_preferences_id'), table_name='property_preferences')
    op.drop_table('property_preferences')
