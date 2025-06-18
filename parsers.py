import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import Grade, DailySchedule


def parse_daily_schedule(contents: bytes, db: Session):
    """
    Parse the `daily_charge_schedule.xlsx` file and upload to database.
    """

    # Perform Pandas pre-processing to obtain DataFrame with columns:
    # ["Date", "Start time", "Grade", "Mould size"]

    df = pd.read_excel(BytesIO(contents), header=[1, 2], na_values=["-", "N/A", ""])
    df = df.stack(level=0, future_stack=True)
    df["Start time"] = pd.to_datetime(df["Start time"], errors="coerce").dt.time
    df.index.set_names([None, "Date"], inplace=True)
    df.reset_index(level="Date", inplace=True)
    df.sort_values(["Date", "Start time"], inplace=True)
    df.dropna(subset=["Start time", "Grade"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # iterate through rows and add entries to DB
    for _, row in df.iterrows():
        grade_name = row["Grade"].strip()
        grade = db.query(Grade).filter_by(name=grade_name).first()
        if not grade:
            # if grade not in "grades" table, add it
            grade = Grade(name=grade_name)
            db.add(grade)
            db.commit()

        daily_charge = (
            db.query(DailySchedule)
            .filter_by(date=row["Date"], time_start=row["Start time"])
            .first()
        )
        if daily_charge:
            msg = f"Start time {row['Start time']} already exists for {row['Date'].date()}."
            raise HTTPException(status_code=400, detail=msg)
        schedule = DailySchedule(
            date=row["Date"],
            time_start=row["Start time"],
            grade_id=grade.id,
            mould_size=row["Mould size"].strip(),
        )
        db.add(schedule)
        db.commit()


def parse_monthly_groups(contents: bytes, db: Session):
    """
    Parse the `product_groups_monthly.xlsx` file and upload to database.
    """
    df = pd.read_excel(BytesIO(contents))

    return


def parse_steel_production(contents: bytes, db: Session):
    """
    Parse the `steel_grade_production.xlsx` file and upload to database.
    """
    df = pd.read_excel(BytesIO(contents))

    return
