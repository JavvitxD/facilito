"""marca de contrasena temporal en usuarios

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Los usuarios que ya existen eligieron su contrasena, asi que no se les
    # exige cambiarla.
    op.add_column(
        'usuarios',
        sa.Column('debe_cambiar_password', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('usuarios', 'debe_cambiar_password')
