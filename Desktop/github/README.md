# Cartão + Vidah - Healthcare Benefits Platform

Uma plataforma completa de cartão de benefícios de saúde e bem-estar construída com React, Express.js e PostgreSQL.

## 🚀 Deploy no Render

### Passos para Deploy:

1. **Faça upload do projeto** para o Render (GitHub, GitLab ou upload direto)

2. **Configure as variáveis de ambiente:**
   - `NODE_ENV`: `production`
   - `DATABASE_URL`: Sua URL do PostgreSQL (fornecida pelo Render)
   - `JWT_SECRET`: Uma chave secreta segura para JWT

3. **O Render executará automaticamente:**
   ```bash
   npm install
   npm run build
   npm start
   ```

### Configuração do Banco de Dados:

1. Crie um PostgreSQL Database no Render
2. Copie a DATABASE_URL para as variáveis de ambiente
3. Execute as migrações: `npm run db:push`

## 📋 Funcionalidades

- ✅ Landing page responsiva com planos de saúde
- ✅ Sistema de captura de leads WhatsApp
- ✅ Painel administrativo secreto (/admin/login)
- ✅ Exportação de dados para campanhas publicitárias
- ✅ Autenticação JWT segura
- ✅ Rate limiting e segurança de produção
- ✅ Badges de desconto em parceiros
- ✅ Detecção automática mobile/desktop para WhatsApp

## 🔐 Acesso Administrativo

- URL: `/admin/login`
- Usuário: `admin`
- Senha: `vidah2025`

## 🏗️ Arquitetura

- **Frontend**: React + TypeScript + Vite
- **Backend**: Express.js + TypeScript
- **Banco**: PostgreSQL + Drizzle ORM
- **Estilo**: Tailwind CSS + shadcn/ui
- **Deploy**: Render (configurado)

## 📱 Contato

- Email: cartaomaisvidah@gmail.com
- WhatsApp: Integração automática no site