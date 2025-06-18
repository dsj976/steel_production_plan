import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session


def parse_daily_schedule(contents: bytes, db: Session):
    """
    Parse the `daily_charge_schedule.xlsx` file and upload to database.
    """
    df = pd.read_excel(BytesIO(contents))

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
