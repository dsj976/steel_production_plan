from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from engine import get_db, init_db


app = FastAPI(
    title="Steel Production Plan API",
    description=(
        "An API to ingest steel production plans in different formats and "
        "forecast next month's production."
    ),
)


@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    filename = file.filename.lower()

    if not filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")


@app.on_event("startup")
def startup_event():
    """Initialize the database on startup."""
    init_db()
