from datetime import date, datetime

from pydantic import BaseModel


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


# Schéma de réponse json pour les requetes
class ProductBase(BaseModel):
    product_name: str
    product_kcal: float | None = None
    product_protein: float | None = None
    product_carbs: float | None = None
    product_fat: float | None = None
    product_fiber: float | None = None
    product_sugar: float | None = None
    product_sodium: float | None = None
    product_chol: float | None = None
    Product_Diet_Tags: str | None = None
    Product_Price_Category: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    Product_ID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    User_mail: str
    User_Subscription: str | None = None
    User_age: int | None = None
    User_weight: float | None = None
    User_Height: float | None = None
    User_gender: str | None = None
    User_Goals: str | None = None
    User_Allergies: str | None = None
    User_Dietary_Preferences: str | None = None
    User_Budget_Level: str | None = None
    User_Injuries: str | None = None


class UserCreate(UserBase):
    User_password: str
    isAdmin: bool = False


class UserLogin(BaseModel):
    User_mail: str
    User_password: str


class UserRead(UserBase):
    User_ID: int
    isAdmin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EquipmentBase(BaseModel):
    Equipment_Name: str
    Equipment_Category: str | None = None
    Equipment_Location: str | None = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentRead(EquipmentBase):
    Equipment_ID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSessionBase(BaseModel):
    User_ID: int
    Session_Date: date
    Session_MaxBpm: int | None = None
    Session_AvgBpm: int | None = None
    Session_RestingBpm: int | None = None
    Session_Duration: int | None = None
    Session_Type: str | None = None
    User_Feedback_Score: int | None = None


class WorkoutSessionCreate(WorkoutSessionBase):
    pass


class WorkoutSessionRead(WorkoutSessionBase):
    Session_ID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MealLogBase(BaseModel):
    User_ID: int
    Product_ID: int
    Log_Date: date


class MealLogCreate(MealLogBase):
    pass


class MealLogRead(MealLogBase):
    Log_ID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BiometricsLogBase(BaseModel):
    User_ID: int
    Log_Date: date
    Weight: float | None = None
    Sleep_Hours: float | None = None
    Heart_Rate: int | None = None


class BiometricsLogCreate(BiometricsLogBase):
    pass


class BiometricsLogRead(BiometricsLogBase):
    Log_ID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
