from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    totp_secret = Column(String(32), nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)
    preferred_language = Column(String(5), default='en')
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    role = relationship("Role", back_populates="users")
    sessions = relationship("Session", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    interventions = relationship("ConsultantIntervention", back_populates="consultant")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # Encrypted sensitive field
    audio_data = Column(Text, nullable=True)  # Base64 encoded audio
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_escalated = Column(Boolean, default=False)
    risk_score = Column(Float, nullable=True)
    risk_tags = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    session = relationship("Session", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    
    def set_content(self, value: str):
        """Encrypt content before storing"""
        from ..security.encryption import encrypt_data
        self.content = encrypt_data(value) if value else None
    
    def get_content(self) -> str:
        """Decrypt content when retrieving"""
        from ..security.encryption import decrypt_data
        return decrypt_data(self.content) if self.content else None

class ConsultantIntervention(Base):
    __tablename__ = "consultant_interventions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    intervention_type = Column(String(50), nullable=False)  # 'contact', 'escalate', 'resolve'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    consultant = relationship("User", back_populates="interventions")
    message = relationship("Message")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    audit_metadata = Column(JSON, nullable=True)
    
    user = relationship("User")

class WellnessLog(Base):
    __tablename__ = "wellness_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    note = Column(Text, nullable=True)  # Encrypted sensitive field
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    patient = relationship("User")
    
    def set_note(self, value: str):
        """Encrypt note before storing"""
        from ..security.encryption import encrypt_data
        self.note = encrypt_data(value) if value else None
    
    def get_note(self) -> str:
        """Decrypt note when retrieving"""
        from ..security.encryption import decrypt_data
        return decrypt_data(self.note) if self.note else None