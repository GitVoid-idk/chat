# 💬 Chat dos Amigos

Chat privado com senha de acesso, nome escolhido pelo usuário e histórico persistente.

## Estrutura

```
chat/
├── main.py              # Backend FastAPI + Socket.IO
├── requirements.txt     # Dependências Python
├── Procfile             # Comando de start (Render)
├── templates/
│   ├── login.html       # Página de login + escolha de nome
│   └── chat.html        # Página do chat
└── data/
    └── mensagens.json   # Histórico salvo (criado automaticamente)
```

## 🚀 Deploy no Render

1. Suba o projeto no GitHub
2. No Render: **New → Web Service**
3. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment**, adicione:
   - `SENHA_ACESSO` → senha que você passa para os amigos
5. Deploy!

## 🔑 Uso

- Acesse o link do Render
- Digite seu nome e a senha do grupo
- Pronto — o histórico fica salvo para todos

> ⚠️ No plano gratuito do Render o arquivo `mensagens.json` é apagado ao reiniciar.
> Para persistência permanente, use um banco de dados externo como o Supabase.
