"""tipo de negocio en empresas

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Las empresas que ya existen son IPS, asi que 'salud' es el valor correcto
    # para todas ellas y nada cambia de aspecto tras la migracion.
    op.add_column(
        'empresas',
        sa.Column('tipo_negocio', sa.String(), nullable=False, server_default='salud'),
    )


def downgrade() -> None:
    op.drop_column('empresas', 'tipo_negocio')
