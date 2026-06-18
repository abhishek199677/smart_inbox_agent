import json
import uuid
from datetime import datetime
from typing import Optional
from openai import OpenAI


class AgentWorker:
    """Universal Worker Model (UWM) base worker.
    Receives a task, plans execution, calls tools/LLM, and returns a result.
    """

    def __init__(self, name: str, model: str = "gpt-4o"):
        self.name = name
        self.model = model
        self.client = OpenAI() if self._api_key_available() else None
        self.session_id: Optional[str] = None
        self.context: dict = {}

    def _api_key_available(self) -> bool:
        import os
        return bool(os.getenv("OPENAI_API_KEY"))

    def start_session(self) -> str:
        self.session_id = str(uuid.uuid4())
        self.context = {"session_start": datetime.utcnow().isoformat(), "history": []}
        return self.session_id

    def plan(self, task: str) -> list[str]:
        steps = [
            f"analyze: understand the intent of the input - '{task}'",
            "classify: categorize the request type (billing, technical, general)",
            "respond: generate an appropriate response using LLM",
            "summarize: create a summary for audit/logging",
        ]
        return steps

    def execute_step(self, step: str, task: str) -> dict:
        step_name = step.split(":")[0].strip()
        if step_name == "analyze":
            return {"step": step_name, "result": f"Analyzing: {task}"}
        elif step_name == "classify":
            category = self._classify_task(task)
            return {"step": step_name, "result": category}
        elif step_name == "respond":
            response = self._generate_response(task)
            return {"step": step_name, "result": response}
        elif step_name == "summarize":
            summary = self._summarize(task)
            return {"step": step_name, "result": summary}
        return {"step": step_name, "result": "unknown step"}

    def _classify_task(self, task: str) -> str:
        if not self.client:
            return "general"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Classify the following support request into exactly one category: billing, technical, or general. Respond with only the category word."},
                    {"role": "user", "content": task},
                ],
                max_tokens=10,
                temperature=0,
            )
            return resp.choices[0].message.content.strip().lower()
        except Exception:
            return "general"

    def _generate_response(self, task: str) -> str:
        if not self.client:
            return f"Thank you for your request. We have received: '{task}' and will get back to you shortly."
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful customer support agent. Respond professionally and concisely to the following support request. Provide a clear answer or next steps."},
                    {"role": "user", "content": task},
                ],
                max_tokens=300,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return f"Thank you for your request: '{task}'. We will follow up shortly."

    def _summarize(self, task: str) -> str:
        words = task.split()
        return f"Request received ({len(words)} words). Category determined. Response generated."

    def run(self, task: str) -> dict:
        self.start_session()
        steps = self.plan(task)
        results = []
        for step in steps:
            result = self.execute_step(step, task)
            results.append(result)
            self.context["history"].append(result)
        return {
            "session_id": self.session_id,
            "task": task,
            "steps": results,
            "final_response": results[2]["result"] if len(results) > 2 else "",
            "category": results[1]["result"] if len(results) > 1 else "unknown",
            "summary": results[3]["result"] if len(results) > 3 else "",
            "status": "completed",
        }


class AgentOrchestrator:
    """Orchestrates multiple workers for complex tasks."""

    def __init__(self):
        self.workers: dict[str, AgentWorker] = {}

    def register_worker(self, name: str, worker: AgentWorker):
        self.workers[name] = worker

    def dispatch(self, worker_name: str, task: str) -> dict:
        worker = self.workers.get(worker_name)
        if not worker:
            return {"error": f"Worker '{worker_name}' not found"}
        return worker.run(task)

    def list_workers(self) -> list[str]:
        return list(self.workers.keys())
