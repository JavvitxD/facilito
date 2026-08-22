"""paquetes

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'paquetes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text()),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'paquete_servicios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('paquete_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('paquetes.id'), nullable=False),
        sa.Column('servicio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('servicios.id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('paquete_servicios')
    op.drop_table('paquetes')
