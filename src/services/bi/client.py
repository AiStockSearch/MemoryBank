import csv
from typing import List, Dict, Optional
from datetime import datetime

class BIClient:
    def __init__(self, target: str = "csv", file_path: str = "bi_data.csv"):
        self.target = target
        self.file_path = file_path

    async def send_data(self, data: List[Dict]) -> Dict:
        if self.target == "csv":
            try:
                if not data:
                    return {"error": "no data"}
                fieldnames = list(data[0].keys())
                file_exists = False
                try:
                    with open(self.file_path, "r") as f:
                        file_exists = True
                except FileNotFoundError:
                    pass
                with open(self.file_path, "a", newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    for row in data:
                        writer.writerow(row)
                return {"status": "ok", "rows": len(data)}
            except Exception as e:
                return {"error": str(e)}
        return {"error": f"target {self.target} not supported"}

    async def get_report(self, metric: str, date_from: str, date_to: str) -> List[Dict]:
        if self.target == "csv":
            try:
                results = []
                with open(self.file_path, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if date_from <= row.get("date", "") <= date_to:
                            results.append(row)
                return results
            except Exception:
                return []
        return [] 