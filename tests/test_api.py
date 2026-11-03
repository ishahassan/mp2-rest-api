
def test_upload_csv(client, sample_csv_bytes):
    # TODO: Upload the sample CSV to POST /upload.
    response = client.post(
        "/upload",
        files={"file": ("sample_data.csv", sample_csv_bytes,"text/csv"
            )
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 6
    assert body["columns"] == 2
    assert isinstance(body["id"], int) and body["id"] > 0
    # Assert status 200, six rows, two columns,
    # and a positive integer dataset ID.


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    # TODO 1: Send a POST request to
    # /datasets/{uploaded_dataset_id}/process
    # using json=processing_body.
    # Assert status 200, one validation removal,
    # and a cleaning report showing 5 → 3 rows.

    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body
    )
    assert response.status_code == 200
    body = response.json()
    assert body["validation_rows_removed"] == 1
    assert body["cleaning_report"]["rows_before"] == 5
    assert body["cleaning_report"]["rows_after"] == 3

    # TODO 2: GET /datasets/{uploaded_dataset_id}.
    # Assert status 200 and total_rows == 3.
    # Check that the returned records contain student IDs
    # 1, 2, and 5 with scores 80, 90, and 85.
    response = client.get(f"/datasets/{uploaded_dataset_id}")
    assert response.status_code == 200
    body = response.json()

    assert body["total_rows"] == 3

    scores_by_student = {row["student_id"]: row["score"] for row in body["data"]}
    assert scores_by_student == {1: 80, 2: 90, 5: 85}


def test_retrieve_missing_dataset(client):
    # TODO: Retrieve a dataset ID that does not exist.
    # Assert status 404.
    response = client.get("/datasets/999")
    assert response.status_code == 404