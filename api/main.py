from datetime import datetime, timedelta, date
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from core.report_generator import generate_report, generate_raw_report
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
    CaloriesInput,
    GymLogInput,
    ExerciseTypeInput,
    ProfileInput,
    WeeklyReportInput,
    BioimpedanceReportInput,
    DexaReportInput,
    BodyMeasurementInput
)
from db.queries import (
    get_user_profile,
    upsert_user_profile,
    get_weekly_reports,
    get_weekly_report,
    upsert_weekly_report,
    get_bioimpedance_reports,
    insert_bioimpedance_report,
    get_dexa_reports,
    insert_dexa_report,
    get_body_measurements,
    insert_body_measurement,
    insert_user,
    get_user_by_email,
    get_weights,
    get_last_weight,
    get_active_phase,
    get_phases,
    update_phase_goals,
    get_calories,
    get_active_calories,
    get_exercise_type,
    insert_exercise_type,
    get_gym_logs,
    get_active_gym_logs,
    close_gym_log,
    insert_gym_log
)

app = FastAPI()

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


# Bioimpedance reports
@app.get("/bioimpedance-reports")
async def get_bioimpedance_reports_ep(user_id: int = Depends(get_current_user_id)):
    return get_bioimpedance_reports(user_id)


@app.post("/bioimpedance-reports")
async def post_bioimpedance_report_ep(data: BioimpedanceReportInput, user_id: int = Depends(get_current_user_id)):
    return insert_bioimpedance_report(user_id, data.model_dump())


# DEXA reports
@app.get("/dexa-reports")
async def get_dexa_reports_ep(user_id: int = Depends(get_current_user_id)):
    return get_dexa_reports(user_id)


@app.post("/dexa-reports")
async def post_dexa_report_ep(data: DexaReportInput, user_id: int = Depends(get_current_user_id)):
    return insert_dexa_report(user_id, data.model_dump())


# Body measurements
@app.get("/body-measurements")
async def get_body_measurements_ep(user_id: int = Depends(get_current_user_id)):
    return get_body_measurements(user_id)


@app.post("/body-measurements")
async def post_body_measurement_ep(data: BodyMeasurementInput, user_id: int = Depends(get_current_user_id)):
    return insert_body_measurement(user_id, data.model_dump())


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


@app.get("/gym/logs")
async def get_gym_logs_ep(user_id: int = Depends(get_current_user_id)):
    return get_gym_logs(user_id)


@app.post("/gym/logs")
async def post_gym_logs_ep(data: GymLogInput, user_id: int = Depends(get_current_user_id)):
    return insert_gym_log(user_id, data.model_dump())


@app.delete("/gym/logs/{log_id}")
async def delete_gym_log_ep(log_id: int, user_id: int = Depends(get_current_user_id)):
    yesterday = datetime.now().date() - timedelta(days=1)
    return close_gym_log(user_id, log_id, yesterday)


@app.patch("/gym/logs/{log_id}")
async def patch_gym_log_ep(log_id: int, data: GymLogInput, user_id: int = Depends(get_current_user_id)):
    return update_gym_log(user_id, log_id, data.model_dump())


# User profile
@app.get("/profile")
async def get_profile_ep(user_id: int = Depends(get_current_user_id)):
    return get_user_profile(user_id)


@app.patch("/profile")
async def patch_profile_ep(data: ProfileInput, user_id: int = Depends(get_current_user_id)):
    return upsert_user_profile(user_id, data.model_dump())


# Weekly reports
@app.get("/weekly-reports")
async def get_weekly_reports_ep(user_id: int = Depends(get_current_user_id)):
    return get_weekly_reports(user_id)


@app.get("/weekly-reports/{week_start}")
async def get_weekly_report_ep(week_start: str, user_id: int = Depends(get_current_user_id)):
    d = date.fromisoformat(week_start)
    return get_weekly_report(user_id, d)


@app.patch("/weekly-reports")
async def patch_weekly_report_ep(data: WeeklyReportInput, user_id: int = Depends(get_current_user_id)):
    return upsert_weekly_report(user_id, data.model_dump())


# AI Report Generator
@app.get("/generate-report")
async def get_ai_report_ep(user_id: int = Depends(get_current_user_id)):
    return PlainTextResponse(generate_report(user_id))


@app.get("/generate-report/raw")
async def get_raw_report_ep(user_id: int = Depends(get_current_user_id)):
    return PlainTextResponse(generate_raw_report(user_id))

# ── Photos ─────────────────────────────────────────────────────────────────────

from api.schemas import PhotoInput
from db.queries import get_photos, get_photos_by_date, get_photo_by_id, insert_photo, delete_photo, get_photo_dates

@app.get("/photos")
async def list_photos(user_id: int = Depends(get_current_user_id)):
    return get_photo_dates(user_id)

@app.get("/photos/{date}")
async def list_photos_by_date(date: str, user_id: int = Depends(get_current_user_id)):
    return get_photos_by_date(user_id, date)

@app.get("/photos/image/{photo_id}")
async def get_photo_image(photo_id: int, user_id: int = Depends(get_current_user_id)):
    photo = get_photo_by_id(user_id, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@app.post("/photos")
async def upload_photo(data: PhotoInput, user_id: int = Depends(get_current_user_id)):
    photo_date = data.date or str(date.today())
    return insert_photo(user_id, photo_date, data.photo_type, data.image_data, data.phase_type)

@app.delete("/photos/{photo_id}")
async def remove_photo(photo_id: int, user_id: int = Depends(get_current_user_id)):
    if delete_photo(user_id, photo_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Photo not found")


# ── AI Report with Photos (ZIP) ───────────────────────────────────────────────

from fastapi.responses import StreamingResponse
import zipfile
import io
import base64

@app.get("/generate-report/zip")
async def generate_report_zip(user_id: int = Depends(get_current_user_id)):
    # Generate the JSON report
    report_json = generate_report(user_id)

    # Get all photos
    photo_dates = get_photo_dates(user_id)
    all_photos = []
    for pd in photo_dates:
        date_str = str(pd["date"])
        date_photos = get_photos_by_date(user_id, date_str)
        for photo in date_photos:
            all_photos.append({
                "filename": f"photos/{date_str}_{photo['photo_type']}.jpg",
                "data": photo["image_data"],
            })

    # Create ZIP in memory
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("weights_report.json", report_json)
        for photo in all_photos:
            try:
                image_bytes = base64.b64decode(photo["data"])
                zf.writestr(photo["filename"], image_bytes)
            except Exception:
                pass

    buffer.seek(0)
    today = date.today().isoformat()
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="weights_report_{today}.zip"'}
    )