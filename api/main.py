from fastapi import FastAPI
from core.weights import parse_weights, add_weight, get_last_weight
from core.phases import parse_phases, update_phase, get_active_phase
from core.reports import  add_report, parse_reports
from api.schemas import WeightInput, PhaseInput, ReportInput

app = FastAPI()

# Weights
@app.get("/weights")
async def get_weights_ep(): 
    return parse_weights()

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
async def get_phases():
    return parse_phases()

@app.post("/phases")
async def post_phase_ep(data: PhaseInput):
    return update_phase(data.model_dump())


# Reports
@app.get("/reports")
async def get_reports():
    return parse_reports()

@app.post("/reports")
async def post_report(data: ReportInput):
    return add_report(data.model_dump())