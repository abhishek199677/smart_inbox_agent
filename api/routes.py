from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from agent_core.worker import AgentWorker, AgentOrchestrator
from agent_core.multi_agent import MultiAgentOrchestrator
from agent_core.memory import InMemoryStore
from agent_core.auth import require_auth
from agent_core.rag import KnowledgeBase
from db.database import DatabaseManager

router = APIRouter()

single_orchestrator = AgentOrchestrator()
support_worker = AgentWorker(name="support-agent")
single_orchestrator.register_worker("support", support_worker)

multi_orchestrator = MultiAgentOrchestrator()

memory_store = InMemoryStore()
db = DatabaseManager()
kb = KnowledgeBase()


class TaskRequest(BaseModel):
    task: str
    worker: str = "support"


class TaskResponse(BaseModel):
    session_id: str
    task: str
    category: str
    final_response: str
    assigned_agent: Optional[str] = None
    rag_used: Optional[bool] = None
    status: str


@router.post("/agent/process")
def process_task(req: TaskRequest, request: Request = None):
    result = multi_orchestrator.process(req.task)

    db.insert_ticket(
        session_id=result["session_id"],
        task=result["task"],
        category=result["category"],
        response=result["final_response"],
    )
    return result


@router.post("/agent/legacy-process", response_model=TaskResponse)
def process_task_legacy(req: TaskRequest):
    result = single_orchestrator.dispatch(req.worker, req.task)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    memory_store.save(result["session_id"], result)
    db.insert_ticket(
        session_id=result["session_id"],
        task=result["task"],
        category=result["category"],
        response=result["final_response"],
    )
    return TaskResponse(**result)


@router.get("/agent/memory/{session_id}")
def get_memory(session_id: str):
    mem = memory_store.get(session_id)
    conv = multi_orchestrator.get_history(session_id)
    if not mem and not conv:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"memory": mem, "conversation": conv}


@router.get("/tickets")
def list_tickets(category: str = None):
    if category:
        return {"tickets": db.search_tickets_by_category(category)}
    return {"tickets": db.get_all_tickets()}


@router.get("/tickets/{session_id}")
def get_ticket(session_id: str):
    ticket = db.get_ticket(session_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/tickets/{session_id}")
def delete_ticket(session_id: str):
    db.delete_ticket(session_id)
    memory_store.delete(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/workers")
def list_workers():
    legacy = [{"name": n, "domain": "general"} for n in single_orchestrator.list_workers()]
    multi = multi_orchestrator.list_agents()
    return {"workers": legacy + multi, "agents": multi}


@router.get("/stats")
def get_stats():
    return {
        "total_tickets": db.count_tickets(),
        "categories": db.category_breakdown(),
    }


@router.post("/rag/search")
def rag_search(query: str, category: str = None):
    results = kb.search(query, category)
    return {"query": query, "category": category, "results": results}


@router.get("/rag/knowledge-base")
def list_kb_categories():
    categories = set(d["category"] for d in kb.documents)
    return {"categories": sorted(categories), "total_docs": len(kb.documents)}


@router.get("/conversations")
def list_conversations():
    return {"sessions": multi_orchestrator.get_all_sessions()}


@router.get("/conversations/{session_id}")
def get_conversation(session_id: str):
    history = multi_orchestrator.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}
