import math

from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import pandas as pd

from engine import get_db, init_db
from forecast import calculate_forecast
from models import Grade, MonthlyBreakdown, Group
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


@app.get("/forecast")
def forecast_production(method: str = "average", db=Depends(get_db)):
    """
    Forecast the grade-level production for the next month
    based on historical data.
    The method can be 'average' or 'weighted_average'.
    """

    try:
        # find grades with production history
        grades = db.query(Grade).filter(Grade.tons != None).all()
        forecasts = []
        for grade in grades:
            # fetch the production history for each grade
            monthly_breakdown = (
                db.query(MonthlyBreakdown)
                .filter_by(grade=grade)
                .order_by(MonthlyBreakdown.month)
            ).all()
            forecast = calculate_forecast(
                monthly_breakdown=monthly_breakdown,
                method=method,
            )
            forecast = math.ceil(
                forecast / 100
            )  # convert tons to number of heats assuming 1 heat = 100 tons
            forecasts.append(
                {"grade": grade.name, "group": grade.group.name, "heats": forecast}
            )

        # forecast month is last month + 1 month
        month = monthly_breakdown[-1].month
        forecast_month = (
            (month.replace(day=1) + pd.DateOffset(months=1)).to_pydatetime().date()
        )

        return {
            "forecast_month": forecast_month.strftime("%Y-%m"),
            "units": "heats",
            "forecast": forecasts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast calculation failed: {e}")


@app.get("/steel_grades")
def get_steel_grades(db=Depends(get_db)):
    """Fetch all steel grades in the grades DB table."""

    try:
        grades = db.query(Grade).all()
        return [
            {
                "id": grade.id,
                "name": grade.name,
                "group": grade.group.name if grade.group else None,
            }
            for grade in grades
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch steel grades: {e}"
        )


@app.get("/product_groups")
def get_product_groups(db=Depends(get_db)):
    """Fetch all product groups in the groups DB table."""

    try:
        groups = db.query(Group).all()
        return [
            {
                "id": group.id,
                "group": group.name,
            }
            for group in groups
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch product groups: {e}"
        )


@app.on_event("startup")
def startup_event():
    """Initialize the database on startup."""
    init_db()
