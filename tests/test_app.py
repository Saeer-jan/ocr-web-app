import io
import tempfile
import time
import unittest
from unittest.mock import patch

from PIL import Image

from app import create_app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app()
        self.app.config.update(TESTING=True, UPLOAD_FOLDER=self.temp_dir.name)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _png_bytes(self):
        image = Image.new("RGB", (10, 10), color="white")
        data = io.BytesIO()
        image.save(data, format="PNG")
        data.seek(0)
        return data

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    @patch("utils.ocr_processor.OCRProcessor.extract_text")
    def test_ocr_job_lifecycle(self, mock_extract):
        mock_extract.return_value = {
            "text": "hello",
            "lines": [{"text": "hello", "confidence": 0.9, "bbox": [[0, 0], [1, 0], [1, 1], [0, 1]]}],
            "language": "en",
            "handwriting_mode": False,
            "engine": "fallback",
        }

        data = {
            "lang": "en",
            "detect_tables": "true",
            "handwriting": "false",
            "file": (self._png_bytes(), "sample.png"),
        }
        response = self.client.post("/api/ocr", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 202)
        job_id = response.get_json()["job_id"]

        for _ in range(50):
            job_response = self.client.get(f"/api/jobs/{job_id}")
            payload = job_response.get_json()
            if payload["status"] == "completed":
                break
            time.sleep(0.02)
        else:
            self.fail("OCR job did not complete")

        self.assertIn("result", payload)
        self.assertEqual(payload["result"]["files"][0]["pages"][0]["text"], "hello")

        export = self.client.get(f"/api/export/{job_id}.json")
        self.assertEqual(export.status_code, 200)
        export.get_data()
        export.close()

    def test_rejects_unsupported_file(self):
        data = {"file": (io.BytesIO(b"x"), "bad.exe")}
        response = self.client.post("/api/ocr", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
