from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from Core.Database import Base


# ---------------------- Database Models ---------------------- #
# Payment history database table
class Payment_History(Base):
    # Database table name
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(100))
    payment_type = Column(String(10))

    # Relationship to owner user
    user = relationship("UserModel", back_populates="payment_history")

    # Object representation for debugging
    def __repr__(self):
        return f"Payment_History(id={self.id}, title={self.title}, amount={self.amount}, description={self.description}, payment_type={self.payment_type})"
