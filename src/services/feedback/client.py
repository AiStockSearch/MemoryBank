import json
from typing import Dict, List, Optional
from datetime import datetime

class FeedbackClient:
    def __init__(self, target: str = "file", file_path: str = "feedback_store.json"):
        self.target = target
        self.file_path = file_path

    async def submit_feedback(self, user: str, text: str, tags: Optional[List[str]] = None) -> Dict:
        feedback = {
            "user": user,
            "text": text,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        if self.target == "file":
            try:
                with open(self.file_path, "a") as f:
                    f.write(json.dumps(feedback, ensure_ascii=False) + "\n")
                return {"status": "ok", "feedback": feedback}
            except Exception as e:
                return {"error": str(e)}
        return {"error": f"target {self.target} not supported"}

    async def get_feedback(self, limit: int = 10) -> List[Dict]:
        if self.target == "file":
            try:
                with open(self.file_path, "r") as f:
                    lines = f.readlines()[-limit:]
                    return [json.loads(line) for line in lines]
            except Exception:
                return []
        return [] 