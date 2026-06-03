from typing import Any, Dict, List, Optional


class OCRProcessor:
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang
        self._engine = None
        self._engine_lang = None

    def _load_engine(self, lang: str):
        if self._engine is not None and self._engine_lang == lang:
            return
        try:
            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=False, show_log=False)
            self._engine_lang = lang
        except Exception:
            self._engine = None
            self._engine_lang = None

    def extract_text(self, image: Any, lang: Optional[str] = None, handwriting: bool = False) -> Dict[str, Any]:
        active_lang = lang or self.default_lang
        self._load_engine(active_lang)

        if self._engine is None:
            return {
                "text": "",
                "lines": [],
                "language": active_lang,
                "handwriting_mode": handwriting,
                "engine": "fallback",
            }

        result = self._engine.ocr(image, cls=True)

        lines: List[Dict[str, Any]] = []
        for block in result or []:
            for item in block or []:
                bbox = item[0]
                text = item[1][0]
                confidence = float(item[1][1])
                lines.append({"text": text, "confidence": confidence, "bbox": bbox})

        return {
            "text": "\n".join(line["text"] for line in lines),
            "lines": lines,
            "language": active_lang,
            "handwriting_mode": handwriting,
            "engine": "paddleocr",
        }
