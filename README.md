# SonnarCrew - Code Analysis Agent

> Um agente inteligente de análise de código powered by OpenAI, desenvolvido em Python com arquitetura moderna e containerizada.

### 🔧 Setup Rápido (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/devjuannobrega/SonnarCrew.git
cd SonnarCrew
```
```

2. **Execute o launcher principal**
```bash
# Windows
start.cmd

# No menu, escolha a opção:
# Depois escolha "Subir stack completa"

## 📋 Visão Geral

O **SonnarCrew** é uma plataforma completa para análise automatizada de código que utiliza IA para fornecer insights profundos sobre qualidade, segurança, performance e boas práticas de desenvolvimento. O projeto combina tecnologias modernas para criar uma experiência de análise de código robusta e escalável.

### 🎯 Principais Funcionalidades

- **Análise de Código com IA**: Utiliza modelos OpenAI (GPT-4, GPT-3.5) para análise inteligente
- **Múltiplas Linguagens**: Suporte a Python, JavaScript, TypeScript, Java, C#, Go, e mais
- **Análise de Segurança**: Detecção de vulnerabilidades e problemas de segurança
- **Métricas de Qualidade**: Complexidade ciclomática, duplicação de código, cobertura
- **API RESTful**: Interface completa para integração com outras ferramentas
- **Interface Web**: Frontend React para visualização e gerenciamento
- **Relatórios Detalhados**: Exportação em múltiplos formatos (PDF, JSON, HTML)
- **Integração CI/CD**: Webhooks e APIs para pipelines de desenvolvimento

## 🏗️ Arquitetura

### Stack Tecnológica

#### Backend
- **Python 3.11+**: Linguagem principal
- **FastAPI**: Framework web moderno e performático
- **SQLAlchemy**: ORM para mapeamento objeto-relacional
- **Alembic**: Migrações de banco de dados
- **OpenAI API**: Integração com modelos de IA
- **AsyncPG**: Driver assíncrono para PostgreSQL
- **Redis**: Cache e gerenciamento de sessões
- **Pydantic**: Validação de dados e serialização

#### Frontend
- **React 18**: Biblioteca para interface de usuário
- **TypeScript**: Tipagem estática para JavaScript
- **Tailwind CSS**: Framework CSS utilitário
- **Axios**: Cliente HTTP para APIs
- **React Router**: Roteamento de páginas
- **React Query**: Gerenciamento de estado e cache

#### Banco de Dados
- **PostgreSQL 15**: Banco de dados principal
- **Redis 7**: Cache e armazenamento temporário

#### DevOps & Infraestrutura
- **Docker**: Containerização de aplicações
- **Docker Compose**: Orquestração de containers
- **Nginx**: Proxy reverso e servidor web
- **GitHub Actions**: CI/CD pipeline
- **Prometheus**: Monitoramento e métricas
- **Grafana**: Dashboards e visualização

### Estrutura do Projeto

```
sonnarcrew/
├── 📁 backend/                    # API Python
│   ├── 📁 app/
│   │   ├── 📁 api/               # Endpoints da API
│   │   ├── 📁 core/              # Configurações core
│   │   ├── 📁 models/            # Modelos de dados
│   │   ├── 📁 services/          # Lógica de negócio
│   │   ├── 📁 utils/             # Utilitários
│   │   └── main.py               # Ponto de entrada
│   ├── 📁 tests/                 # Testes automatizados
│   ├── 📁 migrations/            # Migrações do banco
│   ├── requirements.txt          # Dependências Python
│   └── Dockerfile               # Container do backend
├── 📁 frontend/                  # Interface React
│   ├── 📁 src/
│   │   ├── 📁 components/        # Componentes React
│   │   ├── 📁 pages/            # Páginas da aplicação
│   │   ├── 📁 services/         # Integração com API
│   │   ├── 📁 utils/            # Utilitários frontend
│   │   └── App.tsx              # Componente principal
│   ├── 📁 public/               # Arquivos estáticos
│   ├── package.json             # Dependências Node.js
│   └── Dockerfile              # Container do frontend
├── 📁 database/                 # Scripts de banco
│   ├── 📁 migrations/           # Migrações SQL
│   ├── 📁 seeds/               # Dados iniciais
│   └── init_db.sql             # Inicialização
├── 📁 scripts/                  # Scripts de automação
│   ├── build_docker.py          # Build automation
│   ├── setup_env.cmd           # Configuração ambiente
│   └── run_build.cmd           # Launcher principal
├── 📁 docs/                    # Documentação
├── 📁 logs/                    # Logs da aplicação
├── 📁 uploads/                 # Arquivos de upload
├── 📁 temp/                    # Arquivos temporários
├── docker-compose.yml          # Orquestração Docker
├── .env.example                # Template de configuração
├── .gitignore                  # Arquivos ignorados
└── README.md                   # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos

- **Docker Desktop**: Versão 4.0 ou superior
- **Python 3.8+**: Para scripts de build
- **OpenAI API Key**: Necessária para funcionalidades de IA
- **Git**: Para controle de versão
- **Node.js 16+**: Para desenvolvimento frontend (opcional)
```

4. **Acesse a aplicação**
- API: http://localhost:8000
- Frontend: http://localhost:3000
- PgAdmin: http://localhost:8080
- API Docs: http://localhost:8000/docs

### 📋 Setup Manual

#### 1. Configuração do Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:251081@postgres:5432/code_analysis_db
DB_PASSWORD=251081

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
API_PORT=8000

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
API_SECRET_KEY=your-super-secret-api-key

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

#### 2. Build e Execução

```bash
# Build das imagens
docker compose build

# Subir todos os serviços
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f api
```

### 🛠️ Comandos Úteis

```bash
# Parar todos os serviços
docker compose down

# Rebuild completo
docker compose down && docker compose build --no-cache && docker compose up -d

# Backup do banco de dados
docker exec code_analysis_postgres pg_dump -U postgres code_analysis_db > backup.sql

# Restaurar backup
docker exec -i code_analysis_postgres psql -U postgres code_analysis_db < backup.sql

# Monitorar logs em tempo real
docker compose logs -f

# Executar migrações
docker compose exec api alembic upgrade head

# Acessar shell do container
docker compose exec api bash
```

## 🧪 Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

1. **Virtual Environment Python**
```bash
# Criar virtual environment
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

2. **Desenvolvimento Frontend**
```bash
cd frontend

# Instalar dependências
npm install

# Executar em modo de desenvolvimento
npm start
```

3. **Docker Compose Override**
```bash
# O arquivo docker-compose.override.yml é criado automaticamente
# Contém configurações específicas para desenvolvimento
docker compose up -d
```

### 🧪 Testes

```bash
# Testes do backend
docker compose exec api pytest

# Testes com cobertura
docker compose exec api pytest --cov=app

# Testes do frontend
cd frontend && npm test

# Linting Python
docker compose exec api flake8 app/

# Linting JavaScript
cd frontend && npm run lint
```


### Configurações de Segurança

- **HTTPS**: Configurado para produção
- **CORS**: Configurado para frontends autorizados
- **Input Validation**: Validação rigorosa de dados de entrada
- **SQL Injection Protection**: Uso de ORM com prepared statements

### Variáveis Sensíveis

Nunca commite as seguintes informações:
- `OPENAI_API_KEY`
- `DB_PASSWORD`
- Qualquer credencial em `.env`

## 📈 Performance

### Otimizações Implementadas

- **Cache Redis**: Cache de resultados de análise
- **Async/Await**: Operações assíncronas para melhor concorrência
- **Connection Pooling**: Pool de conexões com banco de dados
- **Query Optimization**: Queries otimizadas com índices apropriados
- **CDN Ready**: Servindo assets estáticos via CDN
- **Gzip Compression**: Compressão de responses HTTP

### Métricas de Performance

- **Response Time**: < 200ms para endpoints básicos
- **Throughput**: > 1000 requests/segundo
- **Memory Usage**: < 512MB por container
- **Database**: Índices otimizados para queries frequentes

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Container não inicia
```bash
# Verificar logs
docker compose logs api

# Verificar recursos
docker system df

# Limpar containers antigos
docker system prune -f
```

#### 2. Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker compose ps postgres

# Reiniciar banco de dados
docker compose restart postgres

# Verificar logs do banco
docker compose logs postgres
```

#### 3. OpenAI API não funciona
```bash
# Verificar variável de ambiente
docker compose exec api env | grep OPENAI

# Testar conexão
docker compose exec api python -c "import openai; print('OpenAI OK')"
```

#### 4. Frontend não carrega
```bash
# Verificar se API está respondendo
curl http://localhost:8000/health

# Verificar logs do frontend
docker compose logs frontend

# Rebuild do frontend
docker compose build frontend --no-cache
```

### Logs e Debugging

```bash
# Logs específicos por serviço
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f postgres

# Debug mode (adicione ao .env)
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🤝 Contribuindo

### Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
4. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. **Push** para a branch (`git push origin feature/AmazingFeature`)
6. **Abra um Pull Request**

### Padrões de Código

- **Python**: Seguir PEP 8
- **JavaScript/TypeScript**: Usar ESLint + Prettier
- **Commits**: Conventional Commits format
- **Testes**: Mínimo 80% de cobertura
- **Documentação**: Docstrings para funções públicas

### Estrutura de Commits

```
feat: add new analysis endpoint
fix: resolve database connection issue
docs: update API documentation
style: format code with black
refactor: optimize query performance
test: add unit tests for analysis service
chore: update dependencies
```

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Juan Nobrega** - *Desenvolvedor Principal* - [@devjuannobrega](https://github.com/devjuannobrega)

## 🙏 Agradecimentos

- OpenAI pela API de IA
- Comunidade FastAPI
- Comunidade React
- Docker Inc.
- PostgreSQL Global Development Group
- Todos os colaboradores do projeto

## 🔄 Roadmap

### Versão 2.1 (Em Desenvolvimento)
- [ ] Integração com GitHub/GitLab
- [ ] Análise de repositórios completos
- [ ] Dashboard de métricas avançado
- [ ] Suporte a mais linguagens

### Versão 2.2 (Planejado)
- [ ] Plugin para VSCode
- [ ] API para integração CI/CD
- [ ] Machine Learning personalizado
- [ ] Análise de performance de código

### Versão 3.0 (Futuro)
- [ ] Clustering e alta disponibilidade
- [ ] Multi-tenancy
- [ ] Analytics avançado
- [ ] Mobile app

---

**Desenvolvido com ❤️ para a comunidade de desenvolvedores**

*SonnarCrew - Transformando análise de código com Inteligência Artificial*
