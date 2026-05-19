from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------- Database Config ---------------------- #
# SQLite database file location
SQLALCHEMY_DATABASE_URI = "sqlite:///../payment.db"
# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       connect_args={"check_same_thread": False},)
# Create session factory
session = sessionmaker(autocommit = False, autoflush = False, bind=engine)
# Base class for all SQLAlchemy models
Base = declarative_base()

# ---------------------- Database Dependency ---------------------- #
# Create and close database session for each request
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

# ---------------------- Database Models ---------------------- #
# Payment history database table
class Payment_History(Base):
    # Database table name
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(100))
    payment_type = Column(String(10))

    # Object representation for debugging
    def __repr__(self):
        return f"Payment_History(id={self.id}, title={self.title}, amount={self.amount}, description={self.description}, payment_type={self.payment_type})"

# ---------------------- Create Tables ---------------------- #
Base.metadata.create_all(engine)