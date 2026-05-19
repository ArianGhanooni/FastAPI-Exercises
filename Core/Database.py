from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URI = "sqlite:///../payment.db"

engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       connect_args={"check_same_thread": False},)
session = sessionmaker(autocommit = False, autoflush = False, bind=engine)
Base = declarative_base()

def get_db():
    db = session()

    try:
        yield db
    finally:
        db.close()

class Payment_History(Base):
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(100))
    payment_type = Column(String(10))

    def __repr__(self):
        return f"Payment_History(id={self.id}, title={self.title}, amount={self.amount}, description={self.description}, payment_type={self.payment_type})"

Base.metadata.create_all(engine)