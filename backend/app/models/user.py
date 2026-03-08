from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    phone = Column(String, unique=True)

    role = Column(String)  # customer | delivery | admin

    # ✅ Phase 12 JWT Password
    password_hash = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
