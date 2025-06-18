import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session

from models import Grade, DailySchedule


def parse_daily_schedule(contents: bytes, db: Session):
    """
    Parse the `daily_charge_schedule.xlsx` file and upload to database.
    """

    # Perform Pandas pre-processing to obtain DataFrame with columns:
    # ["Date", "Start time", "Grade", "Mould size", "Heat"], where
    # "Heat" refers to the heat number of the day.

    df = pd.read_excel(BytesIO(contents), header=[1, 2], na_values=["-", "N/A", ""])
    df = df.stack(level=0, future_stack=True)
    df["Start time"] = pd.to_datetime(df["Start time"], errors="coerce").dt.time
    df.index.set_names([None, "Date"], inplace=True)
    df.reset_index(level="Date", inplace=True)
    df.sort_values(["Date", "Start time"], inplace=True)
    df.dropna(subset=["Start time", "Grade"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["Heat"] = df.groupby("Date")["Start time"].rank(method="first").astype(int)

    # iterate through rows and add entries to DB
    grades = []
    for _, row in df.iterrows():
        grade_name = row["Grade"].strip()
        if grade_name not in grades:
            # if grade not in "grades" table, add it
            grades.append(grade_name)
            grade = db.query(Grade).filter_by(name=grade_name).first()
            if not grade:
                grade = Grade(name=grade_name)
                db.add(grade)

    db.commit()

    return


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
