const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const crypto = require("crypto");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static("public"));

function nomeAleatorio() {
  const adjetivos = ["Rápido", "Silencioso", "Curioso", "Anônimo", "Livre"];
  const animais = ["Lobo", "Falcão", "Raposa", "Pinguim", "Gato"];
  const num = crypto.randomInt(100, 999);
  return `${adjetivos[Math.floor(Math.random() * adjetivos.length)]}${animais[Math.floor(Math.random() * animais.length)]}${num}`;
}

io.on("connection", (socket) => {
  const apelido = nomeAleatorio();
  socket.emit("apelido", apelido);
  io.emit("mensagem", { autor: "Sistema", texto: `${apelido} entrou no chat.` });

  socket.on("mensagem", (texto) => {
    if (typeof texto !== "string" || texto.trim().length === 0) return;
    io.emit("mensagem", { autor: apelido, texto: texto.trim().slice(0, 300) });
  });

  socket.on("disconnect", () => {
    io.emit("mensagem", { autor: "Sistema", texto: `${apelido} saiu.` });
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));
