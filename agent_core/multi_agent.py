from datetime import datetime
from typing import Optional
from openai import OpenAI
from agent_core.rag import KnowledgeBase


class SpecialistAgent:
    """Specialist agent with domain-specific knowledge and RAG context."""

    def __init__(self, name: str, domain: str, system_prompt: str):
        self.name = name
        self.domain = domain
        self.system_prompt = system_prompt
        self.client = OpenAI() if self._has_key() else None
        self.kb = KnowledgeBase()

    def _has_key(self) -> bool:
        import os
        return bool(os.getenv("OPENAI_API_KEY"))

    def process(self, task: str) -> dict:
        rag_context = self.kb.get_context(task, category=self.domain)

        if not self.client:
            return {
                "agent": self.name,
                "response": f"[{self.domain.upper()}] Received: {task}. (Set OPENAI_API_KEY for AI response)",
            }

        messages = [{"role": "system", "content": self.system_prompt}]

        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant knowledge base information:\n{rag_context}",
            })

        messages.append({"role": "user", "content": task})

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
            )
            return {
                "agent": self.name,
                "response": resp.choices[0].message.content.strip(),
                "rag_used": bool(rag_context),
            }
        except Exception as e:
            return {
                "agent": self.name,
                "response": f"Error processing request: {str(e)}",
                "rag_used": False,
            }

    def classify(self, task: str) -> str:
        if not self.client:
            return "general"
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Classify this support request into exactly one category: claims, billing, or general. Respond with only the category word."},
                    {"role": "user", "content": task},
                ],
                max_tokens=10,
                temperature=0,
            )
            return resp.choices[0].message.content.strip().lower()
        except Exception:
            return "general"


class MultiAgentOrchestrator:
    """Routes tasks to the right specialist agent.
    Uses a triage agent to classify, then dispatches to a domain expert.
    """

    def __init__(self):
        self.agents: dict[str, SpecialistAgent] = {}
        self._setup_agents()
        self.conversation_history: dict[str, list] = {}

    def _setup_agents(self):
        self.agents["claims"] = SpecialistAgent(
            name="claims-specialist",
            domain="claims",
            system_prompt=(
                "You are a healthcare claims specialist at an insurance company. "
                "Help the user with claim status, filing, denials, appeals, and documentation. "
                "Use the knowledge base context if provided. Be clear and empathetic."
            ),
        )
        self.agents["billing"] = SpecialistAgent(
            name="billing-specialist",
            domain="billing",
            system_prompt=(
                "You are a medical billing specialist. "
                "Help users with billing questions, payment plans, billing codes, and invoice disputes. "
                "Be professional and provide specific next steps."
            ),
        )
        self.agents["general"] = SpecialistAgent(
            name="general-support",
            domain="general",
            system_prompt=(
                "You are a helpful customer support agent for a healthcare insurance platform. "
                "Answer general questions about the platform, account management, and services. "
                "If a question is outside your scope, suggest the right department."
            ),
        )
        self.triage = SpecialistAgent(
            name="triage-agent",
            domain="general",
            system_prompt="You classify requests for routing.",
        )

    def process(self, task: str) -> dict:
        category = self.triage.classify(task)

        if category not in self.agents:
            category = "general"

        specialist = self.agents[category]
        result = specialist.process(task)

        session_id = f"session-{datetime.utcnow().timestamp()}"
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        self.conversation_history[session_id].append({
            "role": "user",
            "task": task,
            "category": category,
            "agent": specialist.name,
            "response": result["response"],
        })

        return {
            "session_id": session_id,
            "task": task,
            "category": category,
            "assigned_agent": specialist.name,
            "final_response": result["response"],
            "rag_used": result.get("rag_used", False),
            "status": "completed",
        }

    def list_agents(self) -> list[dict]:
        return [
            {"name": a.name, "domain": a.domain}
            for a in self.agents.values()
        ]

    def get_history(self, session_id: str) -> list:
        return self.conversation_history.get(session_id, [])

    def get_all_sessions(self) -> list:
        return list(self.conversation_history.keys())
