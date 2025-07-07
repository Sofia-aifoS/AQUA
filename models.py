from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.types import TypeDecorator
import os
from dotenv import load_dotenv
import uuid

Base = declarative_base()

class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)

class Users(Base):
    __tablename__ = 'users'
    id          = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username    = Column(String(50), unique=True, nullable=False)
    password    = Column(String(255), nullable=False)
    name        = Column(String(255), nullable=True)
    surname     = Column(String(255), nullable=True)
    created_at  = Column(DateTime, nullable=False)
    updated_at  = Column(DateTime, nullable=False)
    chats       = relationship('Chats', back_populates='user')
    messages    = relationship('Messages', back_populates='user')

class Chats(Base):
    __tablename__ = 'chats'
    id          = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id     = Column(GUID(), ForeignKey('users.id'), nullable=False)
    name        = Column(String(1000), nullable=False)
    order       = Column(Integer, nullable=False)
    created_at  = Column(DateTime, nullable=False)
    updated_at  = Column(DateTime, nullable=False)
    user        = relationship('Users', back_populates='chats')
    messages    = relationship('Messages', back_populates='chat')

class Messages(Base):
    __tablename__ = 'messages'
    id          = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id     = Column(GUID(), ForeignKey('users.id'), nullable=False)
    chat_id     = Column(GUID(), ForeignKey('chats.id'), nullable=False)
    message     = Column(String(1000), nullable=False)
    role        = Column(String(255), nullable=False)
    order       = Column(Integer, nullable=False)
    created_at  = Column(DateTime, nullable=False)
    updated_at  = Column(DateTime, nullable=False)
    user        = relationship('Users')
    chat        = relationship('Chats', back_populates='messages')

# Configurazione del database per SQLite
DATABASE_URL = "sqlite:///aqua.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Per creare le tabelle nel database
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)