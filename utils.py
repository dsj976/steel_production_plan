import requests

base_url = "http://localhost:8000"


def upload_excel(file_path: str, url: str = f"{base_url}/upload"):
    """Upload an Excel file (.xlsx) to the database."""
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, files=files)
    return response


def get_forecast(method: str = "average", url: str = f"{base_url}/forecast"):
    """Get the steel production forecast for the next month."""
    response = requests.get(url, params={"method": method})
    return response
