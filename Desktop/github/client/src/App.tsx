import { useEffect } from "react";
import socket from "./lib/socket";

function App() {
  useEffect(() => {
    socket.send("ping");
  }, []);

  return <div>Seu App está funcionando!</div>;
}

export default App;
