*MP2: Rest API*

This project is a FastAPI application that allows users to upload a CSV file, store it in memory, clean it with reusable data-processing modules from MP1, and retrieve the results over HTTP. The API has four endpoints. `GET /health` returns the application status and version. `POST /upload` reads and verifies an uploaded CSV file and returns its dataset ID and metadata. `GET /datasets/{dataset_id}` returns up to `limit` rows from a stored dataset along with the total row count. `POST /datasets/{dataset_id}/process` retrieves, validates, and processes a stored dataset based on a JSON configuration, removing rows with invalid values, duplicates, or missing values. It then returns a cleaning report and replaces the stored data with the processed version. Request middleware assigns each request an ID, logs its method, path, status code, and duration, and returns the ID in an `X-Request-ID` header. The API is covered by pytest tests that exercise the upload, process, and retrieve workflow.

*Run API:*
python -m uvicorn main:app --reload

*Open for Endpoints:* 
http://127.0.0.1:8000/docs

*Run Tests:*
python -m pytest tests -v