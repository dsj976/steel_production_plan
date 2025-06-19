import requests


def upload_excel(file_path: str, base_url: str = "http://localhost:8000"):
    """Upload an Excel file (.xlsx) to the database."""
    url = f"{base_url}/upload"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, files=files)
    return response


def get_forecast(method: str = "average", base_url: str = "http://localhost:8000"):
    """Get the steel production forecast for next month."""
    url = f"{base_url}/forecast"
    response = requests.get(url, params={"method": method})
    return response


def get_db_table(table: str, base_url: str = "http://localhost:8000"):
    """
    Fetch all entries from the specified database table.

    Supported tables:
        - groups: product groups
        - grades: steel grades
    """

    supported_tables = ["groups", "grades"]

    if table == "groups":
        url = f"{base_url}/product_groups"
    elif table == "grades":
        url = f"{base_url}/steel_grades"
    else:
        msg = f"Table '{table}' not supported, must be one of: {supported_tables}."
        raise ValueError(msg)
    response = requests.get(url)

    return response
