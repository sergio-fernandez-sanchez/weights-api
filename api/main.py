from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from core.report_generator import generate_report
from api.auth import hash_password, verify_password, create_token, get_current_user_id
from core.services import (
    update_phase,
    add_weight,
    get_weights_with_phase,
    update_calories,
    update_gym_log
)
from api.schemas import ( 
    UserInput, 
    TokenResponse, 
    WeightInput, 
    PhaseInput, 
    PhaseGoalsInput, 
    ReportInput, 
    CaloriesInput,
    GymLogInput,
    ExerciseTypeInput
)
from db.queries import (
    insert_user,
    get_user_by_email,
    get_weights,
    get_last_weight,
    get_active_phase,
    get_phases,
    get_reports,
    insert_report,
    update_phase_goals,
    get_calories,
    get_active_calories,
    get_exercise_type,
    insert_exercise_type,
    get_active_gym_logs,
    close_gym_log,
    insert_gym_log
    
)

app = FastAPI()

# Midleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost:5174",
                   "https://weights.up.railway.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
@app.post("/auth/register")
async def post_new_user(data: UserInput):
    return insert_user(data.email, hash_password(data.password))


@app.post("/auth/login")
async def login(data: UserInput) -> TokenResponse:
    """
    Verifica las credenciales del usuario y devuelve un token JWT TokenResponse si son correctas.
    Devuelve 401 si el email no existe o la contraseña es incorrecta.
    """
    user_data = get_user_by_email(data.email)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if verify_password(data.password, user_data["password"]):
        return TokenResponse(access_token=create_token(user_data["id"]), token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")   


# Weights
@app.get("/weights")
async def get_weights_ep(user_id: int = Depends(get_current_user_id)): 
    return get_weights(user_id)


@app.get("/weights/last")
async def get_last_weight_ep(user_id: int = Depends(get_current_user_id)):
    return get_last_weight(user_id)


@app.get("/weights/with-phase")
async def get_weights_with_phase_ep(user_id: int = Depends(get_current_user_id)):
    return get_weights_with_phase(user_id)


@app.post("/weights")
async def post_weight_ep(data: WeightInput, user_id: int = Depends(get_current_user_id)): 
    return add_weight(user_id, data.model_dump())


# Phases
@app.get("/phases/active")
async def get_active_phase_ep(user_id: int = Depends(get_current_user_id)):
    return get_active_phase(user_id)


@app.patch("/phases/active")
async def patch_goals_in_active_phase_ep(data: PhaseGoalsInput, user_id: int = Depends(get_current_user_id)):
    return update_phase_goals(user_id, data.model_dump())


@app.get("/phases")
async def get_phases_ep(user_id: int = Depends(get_current_user_id)):
    return get_phases(user_id)


@app.post("/phases")
async def post_phase_ep(data: PhaseInput, user_id: int = Depends(get_current_user_id)):
    return update_phase(user_id, data.model_dump())


# Reports
@app.get("/reports")
async def get_reports_ep(user_id: int = Depends(get_current_user_id)):
    return get_reports(user_id)


@app.post("/reports")
async def post_report_ep(data: ReportInput, user_id: int = Depends(get_current_user_id)):
    return insert_report(user_id, data.model_dump())


# Calories

@app.get("/calories/active")
async def get_active_calories_ep(user_id: int = Depends(get_current_user_id)):
    return get_active_calories(user_id)


@app.get("/calories")
async def get_calories_ep(user_id: int = Depends(get_current_user_id)):
    return get_calories(user_id)


@app.post("/calories")
async def post_calories_ep(data: CaloriesInput, user_id: int = Depends(get_current_user_id)):
    return update_calories(user_id, data.model_dump())


# Exercise types

@app.get("/gym/exercise-types")
async def get_exercise_types_ep(user_id: int = Depends(get_current_user_id)):
    return get_exercise_type(user_id)


@app.post("/gym/exercise-types")
async def post_exercise_types_ep(data: ExerciseTypeInput, user_id: int = Depends(get_current_user_id)):
    return insert_exercise_type(user_id, data.model_dump())


# Gym logs

@app.get("/gym/logs/active")
async def get_active_gym_logs_ep(user_id: int = Depends(get_current_user_id)):
    return get_active_gym_logs(user_id)


@app.post("/gym/logs")
async def post_gym_logs_ep(data: GymLogInput, user_id: int = Depends(get_current_user_id)):
    return insert_gym_log(user_id, data.model_dump())


@app.post("/gym/logs")
async def post_gym_logs_ep(data: GymLogInput, user_id: int = Depends(get_current_user_id)):
    return update_gym_log(user_id, data.model_dump())


@app.delete("/gym/logs/{log_id}")
async def delete_gym_log_ep(log_id: int, user_id: int = Depends(get_current_user_id)):
    return close_gym_log(user_id, log_id, datetime.now().date())

@app.patch("/gym/logs/{log_id}")
async def patch_gym_log_ep(log_id: int, data: GymLogInput, user_id: int = Depends(get_current_user_id)):
    return update_gym_log(user_id, log_id, data.model_dump())


# AI Report Generator
@app.get("/generate-report")
async def get_ai_report_ep(user_id: int = Depends(get_current_user_id)):
    return PlainTextResponse(generate_report(user_id))