from fastapi import FastAPI
from services import update_phase, add_weight
from db.queries import get_weights, get_last_weight, get_active_phase, get_phases, get_reports, insert_report
from api.schemas import WeightInput, PhaseInput, ReportInput

app = FastAPI()

# Weights
@app.get("/weights")
async def get_weights_ep(): 
    return get_weights()

@app.get("/weights/last")
async def get_last_weight_ep():
    return get_last_weight()

@app.post("/weights")
async def post_weight_ep(data: WeightInput): 
    return add_weight(data.model_dump())


# Phases
@app.get("/phases/active")
async def get_active_phase_ep():
    return get_active_phase()

@app.get("/phases")
async def get_phases_ep():
    return get_phases()

@app.post("/phases")
async def post_phase_ep(data: PhaseInput):
    return update_phase(data.model_dump())


# Reports
@app.get("/reports")
async def get_reports_ep():
    return get_reports()

@app.post("/reports")
async def post_report_ep(data: ReportInput):
    return insert_report(data.model_dump())