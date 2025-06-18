from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends

from engine import get_db, init_db
from parsers import parse_daily_schedule, parse_monthly_groups, parse_steel_production


app = FastAPI(
    title="Steel Production Plan API",
    description=(
        "An API to ingest steel production plans in different formats and "
        "forecast next month's production."
    ),
)


@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    filename = file.filename.lower()

    if not filename.endswith(".xlsx"):
        msg = "Only .xlsx files are supported."
        raise HTTPException(status_code=400, detail=msg)

    contents = file.file.read()

    try:
        if "daily_charge_schedule" in filename:
            parse_daily_schedule(contents, db)
        if "product_groups_monthly" in filename:
            parse_monthly_groups(contents, db)
        if "steel_grade_production" in filename:
            parse_steel_production(contents, db)
    except Exception as e:
        msg = f"Failed to parse {filename}: {e}"
        raise HTTPException(status_code=500, detail=msg)


@app.on_event("startup")
def startup_event():
    """Initialize the database on startup."""
    init_db()
