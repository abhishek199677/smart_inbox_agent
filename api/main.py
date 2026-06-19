import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from agent_core.auth import verify_api_key

app = FastAPI(
    title="SmartInbox Agent API",
    description="AI-powered support ticket classification & response agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(verify_api_key)

app.include_router(router, prefix="/api/v1")


react_path = Path(__file__).resolve().parent.parent / "frontend-react" / "index.html"


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "smart-inbox-agent"}


@app.get("/react", response_class=HTMLResponse)
def react_dashboard():
    return FileResponse(react_path)


@app.get("/debug")
def debug():
    return {
        "has_key": bool(os.getenv("OPENAI_API_KEY")),
        "key_prefix": os.getenv("OPENAI_API_KEY", "")[:15] + "...",
        "env_path": str(env_path),
        "env_path_exists": env_path.exists(),
        "cwd": os.getcwd(),
    }


@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SmartInbox Agent - Test</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #1a1a2e; padding: 2rem; max-width: 700px; margin: 0 auto; }
h1 { margin-bottom: 0.5rem; }
p { margin-bottom: 1rem; color: #555; }
textarea { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; resize: vertical; margin-bottom: 0.75rem; }
textarea:focus { outline: none; border-color: #0f3460; }
button { background: #0f3460; color: white; border: none; padding: 0.65rem 1.25rem; border-radius: 8px; font-size: 1rem; cursor: pointer; }
button:hover { background: #1a5276; }
.card { background: white; border-radius: 8px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 1rem; display: none; }
.card.show { display: block; }
.tag { display: inline-block; background: #e8f0fe; color: #0f3460; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
hr { margin: 0.75rem 0; border: 0; border-top: 1px solid #eee; }
pre { white-space: pre-wrap; word-break: break-word; }
</style>
</head>
<body>
<h1>SmartInbox Agent</h1>
<p>Submit a support request below to test the AI agent.</p>
<textarea id="task" rows="3" placeholder="e.g. I was charged twice for my subscription"></textarea>
<button onclick="test()">Submit to Agent</button>
<div id="result" class="card">
<h3>Agent Response</h3>
<p><span class="tag" id="category"></span> <span id="session" style="font-size:0.8rem;color:#888;margin-left:0.5rem;"></span></p>
<hr>
<pre id="response"></pre>
</div>
<script>
function test() {
    var task = document.getElementById('task').value.trim();
    if (!task) return alert('Enter a request');
    var btn = document.querySelector('button');
    btn.disabled = true; btn.textContent = 'Processing...';
    fetch('/api/v1/agent/process', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task: task})
    }).then(function(r){return r.json()}).then(function(d){
        document.getElementById('category').textContent = d.category;
        document.getElementById('session').textContent = 'Session: ' + d.session_id.slice(0,8)+'...';
        document.getElementById('response').textContent = d.final_response;
        document.getElementById('result').classList.add('show');
        document.getElementById('task').value = '';
    }).catch(function(e){alert('Error: '+e.message)})
    .finally(function(){btn.disabled=false;btn.textContent='Submit to Agent'});
}
</script>
</body>
</html>
""")
