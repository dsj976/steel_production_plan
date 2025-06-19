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
