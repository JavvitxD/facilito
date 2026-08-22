"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'empresas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('nit', sa.String()),
        sa.Column('ciudad', sa.String()),
        sa.Column('activa', sa.Boolean(), default=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('rol', sa.String(), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('empresas.id'), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'espacios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('empresas.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('especialidad', sa.String()),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'proveedores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
    )
    op.create_table(
        'insumos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('categoria', sa.String()),
        sa.Column('unidad_medida', sa.String()),
        sa.Column('invima', sa.String()),
        sa.Column('stock_actual', sa.Numeric(12, 4), default=0),
        sa.Column('stock_minimo', sa.Numeric(12, 4), default=0),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'precios_insumo',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('insumo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('insumos.id'), nullable=False),
        sa.Column('proveedor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('proveedores.id'), nullable=False),
        sa.Column('precio_presentacion', sa.Numeric(12, 2), nullable=False),
        sa.Column('unidades_por_presentacion', sa.Integer()),
        sa.Column('descripcion_presentacion', sa.String()),
        sa.Column('fuente_url', sa.String()),
        sa.Column('fecha_precio', sa.Date()),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'servicios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('espacio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('espacios.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text()),
        sa.Column('precio_mercado_referencia', sa.Numeric(12, 2)),
        sa.Column('url_referencia_precio', sa.String()),
        sa.Column('margen_ganancia_pct', sa.Numeric(5, 2), default=30),
        sa.Column('activo', sa.Boolean(), default=True),
    )
    op.create_table(
        'servicio_insumos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('servicio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('servicios.id'), nullable=False),
        sa.Column('insumo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('insumos.id'), nullable=False),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=False),
        sa.Column('notas', sa.String()),
    )


def downgrade() -> None:
    op.drop_table('servicio_insumos')
    op.drop_table('servicios')
    op.drop_table('precios_insumo')
    op.drop_table('insumos')
    op.drop_table('proveedores')
    op.drop_table('espacios')
    op.drop_table('usuarios')
    op.drop_table('empresas')
