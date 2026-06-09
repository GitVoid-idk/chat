const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const fs = require("fs");
const path = require("path");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const HISTORICO_PATH = path.join(__dirname, "historico.json");
const MAX_MENSAGENS = 200;

function carregarHistorico() {
  try {
    if (fs.existsSync(HISTORICO_PATH)) {
      return JSON.parse(fs.readFileSync(HISTORICO_PATH, "utf-8"));
    }
  } catch (e) {}
  return [];
}

function salvarHistorico(historico) {
  fs.writeFileSync(HISTORICO_PATH, JSON.stringify(historico), "utf-8");
}

let historico = carregarHistorico();

app.use(express.static("public"));

io.on("connection", (socket) => {
  // Envia histórico ao conectar
  socket.emit("historico", historico);

  socket.on("entrar", (nome) => {
    if (typeof nome !== "string" || nome.trim().length === 0) return;
    const apelido = nome.trim().slice(0, 30);
    socket.apelido = apelido;

    const msg = { autor: "Sistema", texto: `${apelido} entrou no chat.`, hora: new Date().toISOString() };
    historico.push(msg);
    if (historico.length > MAX_MENSAGENS) historico = historico.slice(-MAX_MENSAGENS);
    salvarHistorico(historico);
    io.emit("mensagem", msg);
  });

  socket.on("mensagem", (texto) => {
    if (!socket.apelido) return;
    if (typeof texto !== "string" || texto.trim().length === 0) return;

    const msg = { autor: socket.apelido, texto: texto.trim().slice(0, 300), hora: new Date().toISOString() };
    historico.push(msg);
    if (historico.length > MAX_MENSAGENS) historico = historico.slice(-MAX_MENSAGENS);
    salvarHistorico(historico);
    io.emit("mensagem", msg);
  });

  socket.on("disconnect", () => {
    if (!socket.apelido) return;
    const msg = { autor: "Sistema", texto: `${socket.apelido} saiu.`, hora: new Date().toISOString() };
    historico.push(msg);
    if (historico.length > MAX_MENSAGENS) historico = historico.slice(-MAX_MENSAGENS);
    salvarHistorico(historico);
    io.emit("mensagem", msg);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));
