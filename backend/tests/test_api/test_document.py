import io
from unittest.mock import patch
from fastapi.testclient import TestClient


# Mocking the IngestionService so we don't load YOLO/Tesseract during unit tests
@patch("app.api.v1.document.IngestionService.process_pdf_document")
def test_upload_pdf_document(mock_process_pdf, client: TestClient):
    """
    Test PDF upload endpoint with mocked AI processing.
    """
    print("Testing: Document (PDF) upload endpoint...")

    # Define what the mocked function should return
    mock_process_pdf.return_value = (
        "[Title]: Mocked Academic Paper\n[Text]: This is a mocked content."
    )

    # Create a dummy file in memory
    dummy_file = io.BytesIO(b"%PDF-1.4 dummy content for testing")
    dummy_file.name = "test_paper.pdf"

    # Send multipart/form-data request
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_paper.pdf", dummy_file, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test_paper.pdf"
    assert data["file_type"] == "pdf"
    assert "id" in data

    # Verify that the mock was actually called
    mock_process_pdf.assert_called_once()
    print("Success: PDF document uploaded and processed via Mock.")


def test_upload_unsupported_document(client: TestClient):
    """
    Test uploading a file type that is not supported (e.g., .txt).
    """
    print("Testing: Unsupported file upload blocking...")
    dummy_file = io.BytesIO(b"Hello world")
    dummy_file.name = "test_file.txt"

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_file.txt", dummy_file, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"
    print("Success: Unsupported file blocked correctly.")
