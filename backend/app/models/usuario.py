import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # 'superadmin' | 'empresa'
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="usuarios")
