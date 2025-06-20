import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const PORT = process.env.PORT || 3000;

// Corrigir __dirname em ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Garantir que DATABASE_URL esteja definida
if (!process.env.DATABASE_URL) {
  console.warn("DATABASE_URL não encontrada. Usando fallback SQLite local.");
  process.env.DATABASE_URL = "file:./local.db";
}

// Servir frontend compilado
app.use(express.static(path.join(__dirname, '../client/dist')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
