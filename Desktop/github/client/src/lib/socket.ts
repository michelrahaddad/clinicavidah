const socket = new WebSocket(import.meta.env.VITE_API_URL);

socket.onopen = () => {
  console.log("✅ WebSocket conectado com sucesso");
};

socket.onerror = (error) => {
  console.error("❌ Erro no WebSocket:", error);
};

export default socket;
