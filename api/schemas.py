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

class CaloriesInput(BaseModel):
    calories: int

class GymLogInput(BaseModel):
    exercise_type_id: int
    weight: Optional[float] = None
    reps: Optional[int] = None

class ExerciseTypeInput(BaseModel):
    name: str
    category: str = 'custom'


class ProfileInput(BaseModel):
    name:        Optional[str]   = None
    birth_date:  Optional[Date]  = None
    sex:         Optional[str]   = None
    height_cm:   Optional[float] = None
    allergies:   Optional[str]   = None
    supplements: Optional[str]   = None


class WeeklyReportInput(BaseModel):
    week_start:         Date
    training_days:      Optional[int]   = None
    avg_daily_steps:    Optional[int]   = None
    alcohol_drinks:     Optional[float] = None
    cigarettes_per_day: Optional[float] = None
    avg_water_liters:   Optional[float] = None
    notes:              Optional[str]   = None

class BioimpedanceReportInput(BaseModel):
    date:                 Optional[Date]  = None
    body_fat_pct:         Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    fat_free_mass:        Optional[float] = None
    visceral_fat_index:   Optional[float] = None
    muscle_quality:       Optional[float] = None
    trunk_fat_kg:         Optional[float] = None
    trunk_fat_pct:        Optional[float] = None
    total_body_water:     Optional[float] = None

class DexaReportInput(BaseModel):
    date:                 Optional[Date]  = None
    fat_mass_kg:          Optional[float] = None
    lean_mass_kg:         Optional[float] = None
    body_fat_pct:         Optional[float] = None
    muscle_mass_kg:       Optional[float] = None
    bone_mineral_density: Optional[float] = None
    visceral_fat_kg:      Optional[float] = None

class BodyMeasurementInput(BaseModel):
    date:         Optional[Date]  = None
    neck_cm:      Optional[float] = None
    shoulders_cm: Optional[float] = None
    chest_cm:     Optional[float] = None
    bicep_cm:     Optional[float] = None
    waist_cm:     Optional[float] = None
    hip_cm:       Optional[float] = None
    thigh_cm:     Optional[float] = None