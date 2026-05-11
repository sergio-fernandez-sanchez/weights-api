from pydantic import BaseModel
from datetime import date as Date
from typing import Optional

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
    start_date: Optional[Date] = None

class PhaseOutput(BaseModel):
    start_date: str
    end_date: str | None = None 
    phase_type: str
    weight_goal: float | None = None 
    date_goal: str | None = None

class PhaseGoalsInput(BaseModel):
    weight_goal: Optional[float] = None
    date_goal: Optional[Date] = None

class ReportInput(BaseModel):
    date: Optional[Date] = None
    body_fat_pct: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    fat_free_mass: Optional[float] = None
    visceral_fat_index: Optional[float] = None
    muscle_quality: Optional[float] = None
    trunk_fat_kg: Optional[float] = None
    trunk_fat_pct: Optional[float] = None
    total_body_water: Optional[float] = None
    neck_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    bicep_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    thigh_cm: Optional[float] = None

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

class CaloriesInput(BaseModel):
    calories: int

class GymLogInput(BaseModel):
    exercise_type_id: int
    weight: Optional[float] = None
    reps: Optional[int] = None

class ExerciseTypeInput(BaseModel):
    name: str
    category: str = 'custom'