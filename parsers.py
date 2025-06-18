import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session


def parse_daily_schedule(contents: bytes, db: Session):
    """
    Parse the `daily_charge_schedule.xlsx` file and upload to database.
    """

    # Perform Pandas operations to obtain DataFrame with columns:
    # ["Date", "Start time", "Grade", "Mould size"]

    df = pd.read_excel(BytesIO(contents), header=[1, 2], na_values=["-", "N/A", ""])
    df = df.stack(level=0, future_stack=True)
    df["Start time"] = pd.to_datetime(df["Start time"], errors="coerce").dt.time
    df.index.set_names([None, "Date"], inplace=True)
    df.reset_index(level="Date", inplace=True)
    df.sort_values(["Date", "Start time"], inplace=True)
    df.dropna(subset=["Start time", "Grade"], inplace=True)
    df.reset_index(drop=True, inplace=True)

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
