from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Group(Base):
    """Table to store product groups."""

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    grades = relationship("Grade", back_populates="group")
    heats = relationship("MonthlyGroupPlan", back_populates="group")

    def __repr__(self):
        return f"Group(name='{self.name}')"


class Grade(Base):
    """Table to store steel grades."""

    __tablename__ = "grades"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    group = relationship("Group", back_populates="grades")
    heats = relationship("DailySchedule", back_populates="grade")
    tons = relationship("MonthlyBreakdown", back_populates="grade")

    def __repr__(self):
        return f"<Grade(name='{self.name}', group='{self.group}')>"


class DailySchedule(Base):
    """Table to store daily schedules."""

    __tablename__ = "daily_schedule"
    __table_args__ = (
        UniqueConstraint("date", "time_start", name="unique_heat_per_day"),
    )

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    mould_size = Column(String(20), nullable=True)

    grade = relationship("Grade", back_populates="heats")

    def __repr__(self):
        return (
            f"<DailySchedule(date='{self.date}', "
            f"time_start='{self.time_start}', "
            f"grade='{self.grade}', "
            f"mould_size='{self.mould_size}')>"
        )


class MonthlyGroupPlan(Base):
    """
    Table to store the number of heats produced each month
    for each product group.
    """

    __tablename__ = "monthly_group_plan"
    __table_args__ = (
        UniqueConstraint("month", "group_id", name="unique_group_per_month"),
    )

    id = Column(Integer, primary_key=True)
    month = Column(Date, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"))
    heats = Column(Integer, nullable=False)

    group = relationship("Group", back_populates="heats")

    def __repr__(self):
        return (
            f"<MonthlyGroupPlan(month='{self.month}', "
            f"group='{self.group}', "
            f"heats='{self.heats}')>"
        )


class MonthlyBreakdown(Base):
    """
    Table to store the monthly breakdown of
    steel grade production.
    """

    __tablename__ = "monthly_breakdown"
    __table_args__ = (
        UniqueConstraint("month", "grade_id", name="unique_grade_per_month"),
    )

    id = Column(Integer, primary_key=True)
    month = Column(Date, nullable=False)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    tons = Column(Integer, nullable=False)

    grade = relationship("Grade", back_populates="tons")

    def __repr__(self):
        return (
            f"<MonthlyBreakdown(month='{self.month}', "
            f"grade='{self.grade}', "
            f"tons='{self.tons}')>"
        )
