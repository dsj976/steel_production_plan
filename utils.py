import requests

base_url = "http://localhost:8000"


def upload_excel(file_path: str, url: str = f"{base_url}/upload"):
    """Upload an Excel file (.xlsx) to the database."""
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, files=files)
    return response
