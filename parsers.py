import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import Grade, DailySchedule


class DailyScheduleParser:
    """
    Parser for the `daily_charge_schedule.xlsx` file.
    """

    def __init__(self, contents: bytes, db: Session):
        self.contents = contents
        self.db = db

    def _read_excel(self):
        """
        Read Excel file and Perform Pandas pre-processing to obtain
        a DataFrame with columns: ["Date", "Start time", "Grade", "Mould size"]
        """

        df = pd.read_excel(
            BytesIO(self.contents), header=[1, 2], na_values=["-", "N/A", ""]
        )
        df = df.stack(level=0, future_stack=True)
        df["Start time"] = pd.to_datetime(df["Start time"], errors="coerce").dt.time
        df.index.set_names([None, "Date"], inplace=True)
        df.reset_index(level="Date", inplace=True)
        df.sort_values(["Date", "Start time"], inplace=True)
        df.dropna(subset=["Start time", "Grade"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        self.df = df

    def _add_to_db(self):
        """
        Iterates through the rows of the DataFrame and adds entries
        to the 'grades' and 'daily_schedule' database tables.
        """
        for _, row in self.df.iterrows():
            grade_name = row["Grade"].strip()
            grade = self.db.query(Grade).filter_by(name=grade_name).first()
            if not grade:
                # if grade not in "grades" table, add it
                grade = Grade(name=grade_name)
                self.db.add(grade)
                self.db.commit()

            daily_charge = (
                self.db.query(DailySchedule)
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
            self.db.add(schedule)
            self.db.commit()

    def __call__(self):
        self._read_excel()
        self._add_to_db()


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
