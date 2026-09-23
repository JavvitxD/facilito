"""ventas y precio de venta en insumos

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('insumos', sa.Column('precio_venta', sa.Numeric(14, 2), nullable=True))

    op.create_table(
        'ventas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('cliente', sa.String(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('estado_pago', sa.String(), nullable=False, server_default='pagado'),
        sa.Column('fecha_pago', sa.Date(), nullable=True),
        sa.Column('total', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('costo_total', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('anulada', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('motivo_anulacion', sa.Text(), nullable=True),
        sa.Column('usuario_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_ventas_espacio_id', 'ventas', ['espacio_id'])
    op.create_index('ix_ventas_fecha', 'ventas', ['fecha'])

    op.create_table(
        'venta_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('venta_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ventas.id'), nullable=False),
        sa.Column('insumo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('insumos.id'), nullable=True),
        sa.Column('servicio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('servicios.id'), nullable=True),
        sa.Column('descripcion', sa.String(), nullable=False),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(14, 2), nullable=False),
        sa.Column('precio_sugerido', sa.Numeric(14, 2), nullable=True),
        sa.Column('costo_unitario', sa.Numeric(14, 2), nullable=True, server_default='0'),
        sa.Column('subtotal', sa.Numeric(14, 2), nullable=False),
    )
    op.create_index('ix_venta_items_venta_id', 'venta_items', ['venta_id'])


def downgrade() -> None:
    op.drop_index('ix_venta_items_venta_id', 'venta_items')
    op.drop_table('venta_items')
    op.drop_index('ix_ventas_fecha', 'ventas')
    op.drop_index('ix_ventas_espacio_id', 'ventas')
    op.drop_table('ventas')
    op.drop_column('insumos', 'precio_venta')
