"""audit_logs

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('entidad', sa.String(), nullable=False),
        sa.Column('entidad_nombre', sa.String(), nullable=True),
        sa.Column('accion', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_audit_logs_espacio_id', 'audit_logs', ['espacio_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_created_at', 'audit_logs')
    op.drop_index('ix_audit_logs_espacio_id', 'audit_logs')
    op.drop_table('audit_logs')
