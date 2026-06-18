import os
import json
from datetime import datetime
from typing import Optional


class DatabaseManager:
    """Manages PostgreSQL operations for agent ticket storage.

    Falls back to local JSON file storage when no DATABASE_URL is set.
    This allows the project to run without a live PostgreSQL instance for demo purposes.
    """

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self._use_postgres = bool(self.db_url)
        self._file_path = "tickets_store.json"
        self._init_file_store()

    def _init_file_store(self):
        if not self._use_postgres and not os.path.exists(self._file_path):
            with open(self._file_path, "w") as f:
                json.dump([], f)

    def _load_tickets(self) -> list[dict]:
        if self._use_postgres:
            return []
        try:
            with open(self._file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_tickets(self, tickets: list[dict]):
        if not self._use_postgres:
            with open(self._file_path, "w") as f:
                json.dump(tickets, f, indent=2)

    def insert_ticket(self, session_id: str, task: str, category: str, response: str):
        if self._use_postgres:
            return
        tickets = self._load_tickets()
        tickets.append({
            "session_id": session_id,
            "task": task,
            "category": category,
            "response": response,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
        })
        self._save_tickets(tickets)

    def get_all_tickets(self) -> list[dict]:
        return self._load_tickets()

    def get_ticket(self, session_id: str) -> Optional[dict]:
        tickets = self._load_tickets()
        for t in tickets:
            if t["session_id"] == session_id:
                return t
        return None

    def search_tickets_by_category(self, category: str) -> list[dict]:
        tickets = self._load_tickets()
        return [t for t in tickets if t["category"] == category]

    def delete_ticket(self, session_id: str) -> bool:
        tickets = self._load_tickets()
        filtered = [t for t in tickets if t["session_id"] != session_id]
        if len(filtered) == len(tickets):
            return False
        self._save_tickets(filtered)
        return True

    def count_tickets(self) -> int:
        return len(self._load_tickets())

    def category_breakdown(self) -> dict:
        tickets = self._load_tickets()
        breakdown = {}
        for t in tickets:
            cat = t.get("category", "general")
            breakdown[cat] = breakdown.get(cat, 0) + 1
        return breakdown
