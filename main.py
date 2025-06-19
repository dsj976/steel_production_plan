from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends

from engine import get_db, init_db
from parsers import DailyScheduleParser, MonthlyGroupParser, SteelProductionParser


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
    """
    Process and upload to the database an Excel file (`.xlsx`) containing steel production data.
    The filename must contain 'daily_charge_schedule', 'product_groups_monthly', or
    'steel_grade_production'.
    """

    filename = file.filename.lower()
    accepted_filenames = [
        "daily_charge_schedule",
        "product_groups_monthly",
        "steel_grade_production", 
    ]

    if not filename.endswith(".xlsx"):
        msg = "Only .xlsx files are supported."
        raise HTTPException(status_code=400, detail=msg)
    if not any(name in filename for name in accepted_filenames):
        msg = (
            "Filename must contain one of the following: "
            f"{', '.join(accepted_filenames)}."
        )
        raise HTTPException(status_code=400, detail=msg)

    contents = file.file.read()

    try:
        if "daily_charge_schedule" in filename:
            daily_schedule_parser = DailyScheduleParser(contents, db)
            daily_schedule_parser()
        elif "product_groups_monthly" in filename:
            monthly_group_parser = MonthlyGroupParser(contents, db)
            monthly_group_parser()
        elif "steel_grade_production" in filename:
            steel_production_parser = SteelProductionParser(contents, db)
            steel_production_parser()
    except Exception as e:
        msg = f"Failed to parse {filename}: {e}"
        raise HTTPException(status_code=500, detail=msg)


@app.on_event("startup")
def startup_event():
    """Initialize the database on startup."""
    init_db()
