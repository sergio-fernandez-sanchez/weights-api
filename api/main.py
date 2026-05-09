from fastapi import FastAPI, HTTPException, Depends
from services import update_phase, add_weight
from db.queries import insert_user, get_user_by_email, get_weights, get_last_weight, get_active_phase, get_phases, get_reports, insert_report
from api.auth import hash_password, verify_password, create_token, get_current_user_id
from api.schemas import UserInput, TokenResponse, WeightInput, PhaseInput, ReportInput

app = FastAPI()

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


@app.post("/weights")
async def post_weight_ep(data: WeightInput, user_id: int = Depends(get_current_user_id)): 
    return add_weight(user_id, data.model_dump())


# Phases
@app.get("/phases/active")
async def get_active_phase_ep(user_id: int = Depends(get_current_user_id)):
    return get_active_phase(user_id)


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
    return insert_report(data.model_dump(), user_id)