import express from 'express';
import path from 'path';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';
import cors from 'cors';

dotenv.config();
const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.static(path.join(__dirname, '../client/dist')));

app.get('*', (_, res) => {
  res.sendFile(path.join(__dirname, '../client/dist/index.html'));
});

const server = app.listen(port, () => {
  console.log('Rotas API registradas');
  console.log('Servindo arquivos estáticos');
  console.log(`[express] serving on port ${port}`);
});

// WebSocket básico
const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  console.log('Cliente WebSocket conectado ✅');

  ws.on('message', (message) => {
    console.log('Mensagem recebida:', message.toString());
    ws.send('Mensagem recebida pelo servidor.');
  });

  ws.on('close', () => {
    console.log('Cliente WebSocket desconectado ❌');
  });
});
