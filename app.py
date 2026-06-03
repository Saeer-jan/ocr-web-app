import json
import os
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from config import Config
from utils.image_processor import load_images_from_file
from utils.ocr_processor import OCRProcessor
from utils.table_detector import TableDetector


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    ocr_processor = OCRProcessor(default_lang=app.config["DEFAULT_LANG"])
    table_detector = TableDetector(enabled=app.config["ENABLE_TABLE_DETECTION"])
    jobs = {}

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    def run_job(job_id: str, saved_files, lang: str, detect_tables: bool, handwriting: bool):
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        output = []
        try:
            for idx, file_path in enumerate(saved_files, start=1):
                images = load_images_from_file(file_path)
                file_results = []
                for page, image in enumerate(images, start=1):
                    result = ocr_processor.extract_text(image=image, lang=lang, handwriting=handwriting)
                    tables = table_detector.detect(result.get("lines", [])) if detect_tables else []
                    result["page"] = page
                    result["tables"] = tables
                    file_results.append(result)
                output.append({"file": Path(file_path).name, "pages": file_results})
                jobs[job_id]["progress"] = min(95, 10 + int((idx / max(len(saved_files), 1)) * 85))

            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["result"] = {
                "job_id": job_id,
                "language": lang,
                "handwriting": handwriting,
                "files": output,
            }
        except Exception as exc:  # pragma: no cover - defensive runtime behavior
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(exc)
            jobs[job_id]["progress"] = 100

    @app.get("/")
    def index():
        return render_template("index.html", languages=app.config["SUPPORTED_LANGS"])

    @app.get("/upload")
    def upload_page():
        return render_template("upload.html", languages=app.config["SUPPORTED_LANGS"])

    @app.get("/results/<job_id>")
    def results_page(job_id):
        return render_template("results.html", job_id=job_id)

    @app.post("/api/ocr")
    def api_ocr():
        files = request.files.getlist("files")
        if not files:
            single_file = request.files.get("file")
            if single_file:
                files = [single_file]

        if not files:
            return jsonify({"error": "No files provided"}), 400

        lang = request.form.get("lang", app.config["DEFAULT_LANG"])
        if lang not in app.config["SUPPORTED_LANGS"]:
            return jsonify({"error": f"Unsupported language: {lang}"}), 400

        detect_tables = request.form.get("detect_tables", "true").lower() == "true"
        handwriting = request.form.get("handwriting", "false").lower() == "true"

        saved_files = []
        for file in files:
            if not file.filename or not allowed_file(file.filename):
                return jsonify({"error": f"Unsupported file: {file.filename}"}), 400
            filename = secure_filename(file.filename)
            target_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{uuid.uuid4()}_{filename}")
            file.save(target_path)
            saved_files.append(target_path)

        job_id = uuid.uuid4().hex
        jobs[job_id] = {"status": "queued", "progress": 0, "result": None}

        thread = threading.Thread(
            target=run_job,
            args=(job_id, saved_files, lang, detect_tables, handwriting),
            daemon=True,
        )
        thread.start()

        return jsonify({"job_id": job_id, "status": "queued"}), 202

    @app.post("/api/ocr/batch")
    def api_ocr_batch():
        return api_ocr()

    @app.get("/api/jobs/<job_id>")
    def api_job(job_id):
        job = jobs.get(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job)

    @app.get("/api/export/<job_id>.<fmt>")
    def api_export(job_id, fmt):
        job = jobs.get(job_id)
        if not job or job.get("status") != "completed":
            return jsonify({"error": "Completed job not found"}), 404

        result = job.get("result", {})
        export_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{job_id}.{fmt}")
        if fmt == "json":
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            mimetype = "application/json"
        elif fmt == "txt":
            lines = []
            for file_item in result.get("files", []):
                lines.append(f"# {file_item['file']}")
                for page in file_item.get("pages", []):
                    lines.append(page.get("text", ""))
                    lines.append("")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            mimetype = "text/plain"
        else:
            return jsonify({"error": "Unsupported export format"}), 400

        return send_file(export_path, mimetype=mimetype, as_attachment=True)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
