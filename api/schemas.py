from pydantic import BaseModel
from datetime import date

class UserInput(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WeightInput(BaseModel):
    weight: float

class WeightOutput(BaseModel):
    date: str
    weight: float

class PhaseInput(BaseModel):
    phase_type: str
    weight_goal: float | None = None 
    date_goal: str | None = None 

class PhaseOutput(BaseModel):
    start_date: str
    end_date: str | None = None 
    phase_type: str
    weight_goal: float | None = None 
    date_goal: str | None = None

class PhaseGoalsInput (BaseModel):
    weight_goal: float | None = None
    date_goal: date | None = None

class ReportInput(BaseModel):
    date: date | None = None
    body_fat_pct: float | None = None
    skeletal_muscle_mass: float | None = None
    fat_free_mass: float | None = None
    visceral_fat_index: float | None = None
    muscle_quality: float | None = None
    trunk_fat_kg: float | None = None
    trunk_fat_pct: float | None = None
    total_body_water: float | None = None
    neck_cm: float | None = None
    chest_cm: float | None = None
    bicep_cm: float | None = None
    hip_cm: float | None = None
    thigh_cm: float | None = None

class ReportOutput(BaseModel):
    date: str
    body_fat_pct: float | None = None
    skeletal_muscle_mass: float | None = None
    fat_free_mass: float | None = None
    visceral_fat_index: float | None = None
    muscle_quality: float | None = None
    trunk_fat_kg: float | None = None
    trunk_fat_pct: float | None = None
    total_body_water: float | None = None
    neck_cm: float | None = None
    chest_cm: float | None = None
    bicep_cm: float | None = None
    hip_cm: float | None = None
    thigh_cm: float | None = None