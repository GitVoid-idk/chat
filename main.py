from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import socketio
import json
import os
from pathlib import Path
from datetime import datetime

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────
SENHA_ACESSO = os.getenv("SENHA_ACESSO", "amigos2024")
DATA_FILE = Path("data/mensagens.json")
DATA_FILE.parent.mkdir(exist_ok=True)
MAX_MENSAGENS = 200

# ─── HELPERS ─────────────────────────────────────────────────────
def carregar_mensagens():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def salvar_mensagens(msgs):
    with open(DATA_FILE, "w") as f:
        json.dump(msgs[-MAX_MENSAGENS:], f, ensure_ascii=False, indent=2)

historico = carregar_mensagens()

def get_sessao(request: Request):
    return request.cookies.get("sessao")

def get_nome(request: Request):
    return request.cookies.get("nome_chat", "")

# ─── FASTAPI + SOCKET.IO ──────────────────────────────────────────
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()
templates = Jinja2Templates(directory="templates")
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

# ─── ROTAS HTTP ───────────────────────────────────────────────────
@fastapi_app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    sessao = get_sessao(request)
    if sessao == "amigo":
        return RedirectResponse("/chat")
    return templates.TemplateResponse("login.html", {"request": request, "erro": None})

@fastapi_app.post("/login", response_class=HTMLResponse)
async def login(request: Request, senha: str = Form(...), nome: str = Form(...)):
    nome = nome.strip()[:30]
    if not nome:
        return templates.TemplateResponse("login.html", {"request": request, "erro": "Digite um nome!"})
    if senha == SENHA_ACESSO:
        resp = RedirectResponse("/chat", status_code=302)
        resp.set_cookie("sessao", "amigo")
        resp.set_cookie("nome_chat", nome)
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "erro": "Senha incorreta. Tenta de novo!"})

@fastapi_app.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("sessao")
    resp.delete_cookie("nome_chat")
    return resp

@fastapi_app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    sessao = get_sessao(request)
    nome = get_nome(request)
    if sessao != "amigo" or not nome:
        return RedirectResponse("/")
    return templates.TemplateResponse("chat.html", {"request": request, "nome": nome, "historico": historico})

# ─── SOCKET.IO ───────────────────────────────────────────────────
nomes_conectados = {}

@sio.event
async def connect(sid, environ, auth):
    pass

@sio.event
async def entrar(sid, data):
    nome = str(data.get("nome", "")).strip()[:30]
    if not nome:
        return
    nomes_conectados[sid] = nome
    msg = {"autor": "Sistema", "texto": f"{nome} entrou no chat.", "hora": datetime.now().strftime("%H:%M")}
    historico.append(msg)
    salvar_mensagens(historico)
    await sio.emit("mensagem", msg)

@sio.event
async def mensagem(sid, data):
    nome = nomes_conectados.get(sid)
    if not nome:
        return
    texto = str(data.get("texto", "")).strip()[:300]
    if not texto:
        return
    msg = {"autor": nome, "texto": texto, "hora": datetime.now().strftime("%H:%M")}
    historico.append(msg)
    salvar_mensagens(historico)
    await sio.emit("mensagem", msg)

@sio.event
async def disconnect(sid):
    nome = nomes_conectados.pop(sid, None)
    if nome:
        msg = {"autor": "Sistema", "texto": f"{nome} saiu.", "hora": datetime.now().strftime("%H:%M")}
        historico.append(msg)
        salvar_mensagens(historico)
        await sio.emit("mensagem", msg)
