const socket = new WebSocket(
  import.meta.env.VITE_API_URL || "wss://seu-backend.onrender.com"
);

socket.addEventListener("open", () => {
  console.log("✅ WebSocket conectado com sucesso");
});

socket.addEventListener("error", (event) => {
  console.error("❌ Erro no WebSocket:", event);
});

socket.addEventListener("message", (event) => {
  console.log("📨 Mensagem recebida:", event.data);
});

export default socket;
