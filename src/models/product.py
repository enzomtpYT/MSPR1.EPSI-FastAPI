from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from src.database import Base

class Product(Base):
    __tablename__ = "products"

    Product_ID = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_kcal = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    product_protein = Column(Float, nullable=True)
    product_carbs = Column(Float, nullable=True)
    product_fat = Column(Float, nullable=True)
    product_fiber = Column(Float, nullable=True)
    product_sugar = Column(Float, nullable=True)
    product_sodium = Column(Float, nullable=True)
    product_chol = Column(Float, nullable=True)
    Product_Diet_Tags = Column(String, nullable=True)
    Product_Price_Category = Column(String, nullable=True)
