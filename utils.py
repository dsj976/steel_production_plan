import requests


def upload_excel(file_path: str, base_url: str = "http://localhost:8000"):
    """Upload an Excel file (.xlsx) to the database."""

    url = f"{base_url}/upload"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, files=files)
    return response


def get_forecast(
    base_url: str = "http://localhost:8000",
):
    """
    Get the grade-level production forecast for next month.
    """

    url = f"{base_url}/forecast"
    response = requests.get(url)
    return response


def get_db_table(table: str, base_url: str = "http://localhost:8000"):
    """
    Fetch all entries from the specified database table.

    Supported tables:
        - groups: product groups
        - grades: steel grades
        - daily_schedules: daily production schedules of steel grades
        - monthly_plans: monthly production plans of heats per product group
        - monthly_breakdown: monthly production breakdown of tons per steel grade
    """

    supported_tables = [
        "groups",
        "grades",
        "daily_schedules",
        "monthly_plans",
        "monthly_breakdown",
    ]

    if table == "groups":
        url = f"{base_url}/product_groups"
    elif table == "grades":
        url = f"{base_url}/steel_grades"
    elif table == "daily_schedules":
        url = f"{base_url}/daily_schedules"
    elif table == "monthly_plans":
        url = f"{base_url}/monthly_plans"
    elif table == "monthly_breakdown":
        url = f"{base_url}/monthly_breakdown"
    else:
        msg = f"Table '{table}' not supported, must be one of: {supported_tables}."
        raise ValueError(msg)
    response = requests.get(url)

    return response
