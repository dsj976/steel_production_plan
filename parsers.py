from typing import Any
import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import Grade, DailySchedule, Group, MonthlyGroupPlan


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
        to the 'grades' and 'daily_schedule' database tables. Raises
        error if a start time already exists for a given date in the
        table.
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


class MonthlyGroupParser:
    """
    Parser for the `product_groups_monthly.xlsx` file.
    """

    def __init__(self, contents: bytes, db: Session):
        self.contents = contents
        self.db = db

    def _read_excel(self):
        """
        Read Excel file and perform Pandas pre-processing to obtain
        a DataFrame with columns corresponding to different group names,
        indexed by date.
        """
        df = pd.read_excel(BytesIO(self.contents), header=1, na_values=["-", "N/A", ""])
        df.set_index(df.columns[0], inplace=True)
        df = df.transpose()
        df.columns.set_names(None, inplace=True)
        df.index.set_names("Date", inplace=True)
        # round the "Date" index to start of the month
        df.index = pd.to_datetime(df.index).to_period("M").to_timestamp()

        self.df = df

    def _add_to_db(self):
        """
        Adds new quality groups to to the 'groups' table and
        monthly group plans to the 'monthly_group_plan' table
        by looping through the pre-processed DataFrame. Raises
        error if monthly plan for given group and month already
        exists in the table.
        """

        for group_name in self.df.columns:
            group = self.db.query(Group).filter_by(name=group_name.strip()).first()
            if not group:
                # if group not in "groups" table, add it
                group = Group(name=group_name.strip())
                self.db.add(group)
                self.db.commit()
            for month, heats in self.df[group_name].items():
                monthly_plan = (
                    self.db.query(MonthlyGroupPlan)
                    .filter_by(month=month.date(), group=group)
                    .first()
                )
                if monthly_plan:
                    msg = f"An entry already exists for {group_name} for {month.date()}"
                    raise HTTPException(status_code=400, detail=msg)
                monthly_plan = MonthlyGroupPlan(
                    month=month.date(), group_id=group.id, heats=heats
                )
                self.db.add(monthly_plan)
                self.db.commit()

    def __call__(self):
        self._read_excel()
        self._add_to_db()


def parse_steel_production(contents: bytes, db: Session):
    """
    Parse the `steel_grade_production.xlsx` file and upload to database.
    """
    df = pd.read_excel(BytesIO(contents))

    return
