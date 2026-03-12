from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
import time

class TaskStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    app_id: int
    name: str
    status: TaskStatus = TaskStatus.PENDING
    retries: int = 0
    last_updated: float = 0.0
    error_msg: Optional[str] = None

    def mark_success(self):
        self.status = TaskStatus.SUCCESS
        self.last_updated = time.time()
        self.error_msg = None

    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.last_updated = time.time()
        self.error_msg = error
        self.retries += 1

    def mark_skipped(self, reason: str):
        self.status = TaskStatus.SKIPPED
        self.last_updated = time.time()
        self.error_msg = reason

    def to_dict(self) -> Dict:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "status": self.status.value,
            "retries": self.retries,
            "last_updated": self.last_updated,
            "error_msg": self.error_msg
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            app_id=data["app_id"],
            name=data["name"],
            status=TaskStatus(data["status"]),
            retries=data.get("retries", 0),
            last_updated=data.get("last_updated", 0.0),
            error_msg=data.get("error_msg")
        )
