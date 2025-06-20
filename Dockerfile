FROM python:3.12-slim

WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

# run the app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
