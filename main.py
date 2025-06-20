import math

from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import pandas as pd

from engine import get_db, init_db
from forecast import calculate_forecast
from models import Grade, MonthlyBreakdown, Group, DailySchedule, MonthlyGroupPlan
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
def forecast_production(db=Depends(get_db)):
    """
    Forecast the production of heats at grade level
    for the next month based on historical data.
    """

    try:
        groups = db.query(Group).all()
        forecasts = {}
        for group in groups:
            grades = db.query(Grade).filter_by(group=group)
            # filter the grades that have production history
            grades = grades.filter(Grade.tons != None).all()
            # get all breakdowns for these grades
            grade_ids = [grade.id for grade in grades]
            breakdowns = (
                db.query(MonthlyBreakdown)
                .filter(MonthlyBreakdown.grade_id.in_(grade_ids))
                .order_by(MonthlyBreakdown.month)
                .all()
            )
            # get the production plan for this group
            plans = (
                db.query(MonthlyGroupPlan)
                .filter_by(group_id=group.id)
                .order_by(MonthlyGroupPlan.month)
                .all()
            )

            group_heats_by_month = {plan.month: plan.heats for plan in plans}

            # assumption: 1 heat equals 100 tons
            grade_heats_by_month = {}
            for b in breakdowns:
                if b.month not in grade_heats_by_month:
                    grade_heats_by_month[b.month] = {}
                grade_heats_by_month[b.month][b.grade_id] = b.tons / 100

            # for each steel grade, calculate its historical production
            # ratio relative to its group
            mean_ratios = {}  # keys will be different steel grade ids
            for grade in grades:
                ratios = []
                for month, heats_by_grade in grade_heats_by_month.items():
                    if grade.id in heats_by_grade and month in group_heats_by_month:
                        heats = group_heats_by_month[month]
                        if heats and heats > 0:
                            ratio = heats_by_grade[grade.id] / heats
                            ratios.append(ratio)
                mean_ratios[grade.id] = sum(ratios) / len(ratios) if ratios else None

            # the forecast month should be the last month in the group production
            # plans, and should not be contained in the grade breakdowns
            forecast_month = list(group_heats_by_month.keys())
            forecast_month = forecast_month[-1]
            if forecast_month in grade_heats_by_month.keys():
                print("Warning: no month to forecast.")
                continue

            # apply the ratios calculated above to the group production plan
            # for the forecast month
            forecast_heats = group_heats_by_month[forecast_month]
            forecast = dict.fromkeys(("grade", "heats"))
            for grade in grades:
                forecast["grade"] = grade.name
                ratio = mean_ratios[grade.id]
                if ratio is not None:
                    forecast["heats"] = int(round(ratio * forecast_heats))
                else:
                    forecast["heats"] = None
            forecasts[group.name] = {
                "forecast_month": forecast_month.strftime("%Y-%m"),
                "forecast": forecast,
            }

        return forecasts

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


@app.get("/daily_schedules")
def get_daily_schedules(db=Depends(get_db)):
    """Fetch the daily schedules from the daily_schedule DB table."""

    try:
        schedules = (
            db.query(DailySchedule)
            .order_by(DailySchedule.date, DailySchedule.time_start)
            .all()
        )
        result = {}
        for sched in schedules:
            date_str = sched.date.strftime("%Y-%m-%d")
            if date_str not in result:
                result[date_str] = []
            result[date_str].append(
                {
                    "time_start": sched.time_start.strftime("%H:%M")
                    if sched.time_start
                    else None,
                    "grade": sched.grade.name if sched.grade else None,
                    "mould_size": sched.mould_size,
                }
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch daily schedules: {e}"
        )


@app.get("/monthly_plans")
def get_monthly_plan(db=Depends(get_db)):
    """Fetch monthly plans from the monthly_group_plan DB table."""

    try:
        plans = (
            db.query(MonthlyGroupPlan)
            .order_by(MonthlyGroupPlan.month, MonthlyGroupPlan.group_id)
            .all()
        )
        result = {}
        for plan in plans:
            month_str = plan.month.strftime("%Y-%m")
            if month_str not in result:
                result[month_str] = []
            result[month_str].append(
                {
                    "group": plan.group.name if plan.group else None,
                    "heats": plan.heats,
                }
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch monthly plans: {e}"
        )


@app.get("/monthly_breakdown")
def get_monthly_breakdown(db=Depends(get_db)):
    """Fetch the monthly production breakdown from the monthly_breakdown DB table."""

    try:
        breakdowns = (
            db.query(MonthlyBreakdown)
            .order_by(MonthlyBreakdown.month, MonthlyBreakdown.grade_id)
            .all()
        )
        result = {}
        for b in breakdowns:
            month_str = b.month.strftime("%Y-%m")
            if month_str not in result:
                result[month_str] = []
            result[month_str].append(
                {
                    "grade": b.grade.name if b.grade else None,
                    "tons": b.tons,
                }
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch monthly breakdown: {e}"
        )


@app.on_event("startup")
def startup_event():
    """Initialize the database on startup."""
    init_db()
