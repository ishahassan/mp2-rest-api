
import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging
from data_pipeline import create_cleaning_report, process_data, validate_dataframe
from src.models import ProcessingReport, ProcessConfig

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": app.version}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".csv":
        logger.warning(f"Unsupported file format: {suffix}")
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format '{suffix}'. Please upload a .csv file.")
    
    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.EmptyDataError:
        logger.warning(f"Empty CSV file: {file.filename}")
        raise HTTPException(status_code=400, detail="The CSV file is empty.")
    except pd.errors.ParserError:
        logger.warning(f"Could not parse CSV file: {file.filename}")
        raise HTTPException(status_code=400, detail="The file could not be parsed as a valid CSV.")
    except UnicodeDecodeError:
        logger.warning(f"Could not decode CSV file: {file.filename}")
        raise HTTPException(status_code=400, detail="The file could not be decoded. Please upload a UTF-8 encoded CSV file.")
    
    dataset_id = storage.save(df, file.filename)
    logger.info(f"Uploaded dataset: id={dataset_id}, filename={file.filename}, rows={len(df)}")
    return storage.get_metadata(dataset_id)
    
@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, 
                            detail=f"Dataset {dataset_id} not found.")
    records = json.loads(df.head(limit).to_json(orient="records"))
    logger.info(f"Retrieved dataset: id={dataset_id}, returned_rows={len(records)}")
    return {"id": dataset_id, "data": records, "total_rows": len(df)}

@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport 
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    # TODO: retrieve, validate, process, report, update, and return.

    # Retrieve dataset
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found.")

    # Validate the dataset
    config_dict = config.model_dump()
    validation = config_dict["validation"]

    missing_numeric = [c for c in validation["numeric_columns"] if c not in df.columns]
    if missing_numeric:
        logger.warning(f"Missing numeric columns: {missing_numeric}")
        raise HTTPException(status_code=400, detail=f"Missing required numeric columns: {missing_numeric}")

    rows_before_validation = len(df)

    try:
        validated_df = validate_dataframe(
            df,
            validation["required_columns"],
            validation["numeric_columns"],
        )
        validation_removed = rows_before_validation - len(validated_df)
        validated_copy = validated_df.copy()

        # Process the dataset
        processed_df = process_data(validated_df, config_dict)

        # Create the cleaning report
        report = create_cleaning_report(validated_copy, processed_df)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Update the stored dataset
    storage.update(dataset_id, processed_df)
    logger.info(
        f"Processed dataset: id={dataset_id}, validation_removed={validation_removed}, "
        f"rows_before={report['rows_before']}, rows_after={report['rows_after']}"
    )

    # Return the processing report
    return {
        "id": dataset_id,
        "validation_rows_removed": validation_removed,
        "cleaning_report": report
    }