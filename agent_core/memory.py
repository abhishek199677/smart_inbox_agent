import json
from datetime import datetime
from typing import Optional


class InMemoryStore:
    """Simple in-memory key-value store for agent context and session memory."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def save(self, key: str, value: dict) -> None:
        self._store[key] = {**value, "_saved_at": datetime.utcnow().isoformat()}

    def get(self, key: str) -> Optional[dict]:
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def list_keys(self) -> list[str]:
        return list(self._store.keys())

    def search_by_category(self, category: str) -> list[dict]:
        return [v for v in self._store.values() if v.get("category") == category]


class ConversationMemory:
    """Manages conversation history for context-aware agent interactions."""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._sessions: dict[str, list[dict]] = {}

    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(self._sessions[session_id]) > self.max_history:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
