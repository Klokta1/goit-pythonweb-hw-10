from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="contacts")

    def __repr__(self):
        return f"<Contact {self.first_name} {self.last_name}>"
