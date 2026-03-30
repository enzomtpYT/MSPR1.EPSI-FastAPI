from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.product import Product
from src.models.user import User
from src.schemas import ProductCreate, ProductRead
from src.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate, db: DB, current_user: CurrentUser):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=list[ProductRead])
def get_products(db: DB, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    # Return all products (shared nutritional database)
    return db.query(Product).offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: DB, current_user: CurrentUser):
    product = db.query(Product).filter(Product.Product_ID == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductCreate, db: DB, current_user: CurrentUser):
    product = db.query(Product).filter(Product.Product_ID == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: DB, current_user: CurrentUser):
    product = db.query(Product).filter(Product.Product_ID == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    db.commit()
