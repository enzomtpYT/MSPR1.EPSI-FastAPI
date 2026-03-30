from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.equipment import Equipment
from src.models.user import User
from src.schemas import EquipmentCreate, EquipmentRead
from src.auth import get_current_user

router = APIRouter(prefix="/equipment", tags=["equipment"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=EquipmentRead, status_code=201)
def create_equipment(equipment: EquipmentCreate, db: DB, current_user: CurrentUser):
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    # Associate equipment with current user
    current_user.equipment.append(db_equipment)
    db.commit()
    return db_equipment


@router.get("/", response_model=list[EquipmentRead])
def get_equipment(db: DB, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    # Return only equipment associated with the current user
    return current_user.equipment[skip : skip + limit]


@router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment_by_id(equipment_id: int, db: DB, current_user: CurrentUser):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    # Check if user has access to this equipment
    if equipment not in current_user.equipment:
        raise HTTPException(403, "Access denied to this equipment")
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentRead)
def update_equipment(equipment_id: int, payload: EquipmentCreate, db: DB, current_user: CurrentUser):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    # Check if user has access to this equipment
    if equipment not in current_user.equipment:
        raise HTTPException(403, "Access denied to this equipment")
    for key, value in payload.model_dump().items():
        setattr(equipment, key, value)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: int, db: DB, current_user: CurrentUser):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    # Check if user has access to this equipment
    if equipment not in current_user.equipment:
        raise HTTPException(403, "Access denied to this equipment")
    current_user.equipment.remove(equipment)
    db.commit()
