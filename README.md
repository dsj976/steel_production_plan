# An API and database for a steel plant's production plans

This repository provides a backend API and database schema to upload a steel plant's production plans, and to forecast the number of heats of each steel grade for next month.

## Getting started

### Cloning the repository

```bash
git clone git@github.com:dsj976/steel_production_plan.git
cd steel_production_plan
cd input_files
unzip archive.zip  # unzip the Excel files that will be uploaded to the DB 
```

### Running the app inside a Docker container (recommended)

If you want to avoid a local installation of the package, it is recommended to use a Docker container to serve the app.

From repo root directory, run the following command to build a Docker image called `steel_production_plan`.

```bash
docker build -t steel_production_plan .
```

You can then run the container as a background process exposing port 8000:

```bash
docker run -d -p 8000:8000 steel_production_plan
```

This will serve the API at http://localhost:8000/docs. You can access the API at this URL to see all available endpoints. 

### Running the app locally

Alternatively, you can install the requirements inside a Python virtual environment, and serve the app locally:

From the repo root directory, run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Once you have installed all requirements, you can serve the app by running:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

This will serve the API at http://localhost:8000/docs.

## Next steps

Check out the `api_demo.ipynb` notebook for a demo on how to use the API.
