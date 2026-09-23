"""caja: movimientos, prestamos, abonos y arqueos

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'movimientos_caja',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('categoria', sa.String(), nullable=False),
        sa.Column('concepto', sa.String(), nullable=False),
        sa.Column('monto', sa.Numeric(14, 2), nullable=False),
        sa.Column('referencia_tipo', sa.String(), nullable=True),
        sa.Column('referencia_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('anulado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('motivo_anulacion', sa.Text(), nullable=True),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_movimientos_caja_espacio_id', 'movimientos_caja', ['espacio_id'])
    op.create_index('ix_movimientos_caja_fecha', 'movimientos_caja', ['fecha'])

    op.create_table(
        'prestamos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('deudor', sa.String(), nullable=False),
        sa.Column('concepto', sa.String(), nullable=True),
        sa.Column('monto', sa.Numeric(14, 2), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_prestamos_espacio_id', 'prestamos', ['espacio_id'])

    op.create_table(
        'abonos_prestamo',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('prestamo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('prestamos.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('monto', sa.Numeric(14, 2), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_abonos_prestamo_prestamo_id', 'abonos_prestamo', ['prestamo_id'])

    op.create_table(
        'arqueos_caja',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('efectivo_contado', sa.Numeric(14, 2), nullable=False),
        sa.Column('saldo_teorico', sa.Numeric(14, 2), nullable=False),
        sa.Column('diferencia', sa.Numeric(14, 2), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_arqueos_caja_espacio_id', 'arqueos_caja', ['espacio_id'])


def downgrade() -> None:
    op.drop_index('ix_arqueos_caja_espacio_id', 'arqueos_caja')
    op.drop_table('arqueos_caja')
    op.drop_index('ix_abonos_prestamo_prestamo_id', 'abonos_prestamo')
    op.drop_table('abonos_prestamo')
    op.drop_index('ix_prestamos_espacio_id', 'prestamos')
    op.drop_table('prestamos')
    op.drop_index('ix_movimientos_caja_fecha', 'movimientos_caja')
    op.drop_index('ix_movimientos_caja_espacio_id', 'movimientos_caja')
    op.drop_table('movimientos_caja')
