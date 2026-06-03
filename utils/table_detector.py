from typing import Dict, List


class TableDetector:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def detect(self, lines: List[Dict]) -> List[Dict]:
        if not self.enabled or not lines:
            return []

        rows = []
        for line in lines:
            text = str(line.get("text", "")).strip()
            if not text:
                continue
            if "\t" in text:
                cells = [c.strip() for c in text.split("\t") if c.strip()]
            else:
                cells = [c.strip() for c in text.split("  ") if c.strip()]
            if len(cells) >= 2:
                rows.append({"cells": cells, "bbox": line.get("bbox")})

        return [{"row_count": len(rows), "rows": rows}] if rows else []
