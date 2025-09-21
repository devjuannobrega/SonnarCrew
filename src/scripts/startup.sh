#!/bin/bash

# Script de inicialização para o Code Analysis Agent
# Este script configura o ambiente e inicia a aplicação

set -e  # Para execução em caso de erro

echo "🚀 Iniciando Code Analysis Agent..."
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    log_error "Python3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
log_info "Versão do Python: $PYTHON_VERSION"

# Verificar se está no diretório correto
if [ ! -f "main.py" ]; then
    log_error "main.py não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs
log_info "Diretório de logs criado/verificado"

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        log_warning "Arquivo .env não encontrado. Copiando de .env.example..."
        cp .env.example .env
        log_info "Arquivo .env criado. Por favor, configure suas variáveis de ambiente."
    else
        log_warning "Nem .env nem .env.example encontrados. Usando configurações padrão."
    fi
fi

# Verificar se virtual environment existe
if [ ! -d "venv" ]; then
    log_info "Criando virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment criado"
fi

# Ativar virtual environment
log_info "Ativando virtual environment..."
source venv/bin/activate

# Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
if [ -f "requirements.txt" ]; then
    log_info "Instalando dependências..."
    pip install -r requirements.txt
    log_success "Dependências instaladas"
else
    log_error "requirements.txt não encontrado"
    exit 1
fi

# Verificar se Docker está rodando (para PostgreSQL)
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        log_info "Docker está rodando"

        # Verificar se PostgreSQL container está rodando
        if docker ps | grep -q "postgres"; then
            log_success "PostgreSQL container está rodando"
        else
            log_warning "PostgreSQL container não encontrado"
            log_info "Iniciando serviços Docker..."

            if [ -f "docker-compose.yml" ]; then
                docker-compose up -d postgres
                log_info "Aguardando PostgreSQL inicializar..."
                sleep 10
                log_success "PostgreSQL iniciado"
            else
                log_error "docker-compose.yml não encontrado"
                exit 1
            fi
        fi
    else
        log_warning "Docker não está rodando. Certifique-se de que o PostgreSQL está disponível."
    fi
else
    log_warning "Docker não encontrado. Certifique-se de que o PostgreSQL está disponível."
fi

# Executar testes de conectividade
log_info "Testando conectividade com banco de dados..."
python3 -c "
import asyncio
import sys
import os
sys.path.append('.')

async def test_db():
    try:
        from src.database.database import create_tables
        await create_tables()
        print('✅ Conectividade com banco de dados: OK')
        return True
    except Exception as e:
        print(f'❌ Erro na conectividade com banco: {e}')
        return False

result = asyncio.run(test_db())
sys.exit(0 if result else 1)
" || {
    log_error "Falha na conectividade com banco de dados"
    log_info "Verifique se PostgreSQL está rodando e as configurações em .env estão corretas"
    exit 1
}

# Testar agente de análise
log_info "Testando agente de análise..."
python3 -c "
import asyncio
import sys
sys.path.append('.')

async def test_agent():
    try:
        from src.agents.code_analyzer_agent import CodeAnalyzerAgent
        agent = CodeAnalyzerAgent()
        result = await agent.analyze_code('print(\"Hello, World!\")')
        print('✅ Agente de análise: OK')
        return True
    except Exception as e:
        print(f'❌ Erro no agente de análise: {e}')
        return False

result = asyncio.run(test_agent())
sys.exit(0 if result else 1)
" || {
    log_error "Falha no teste do agente de análise"
    exit 1
}

log_success "Todos os testes passaram!"

echo ""
read -p "Deseja iniciar o servidor agora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Iniciando servidor..."
    echo ""
    echo "📡 Servidor será iniciado em http://localhost:8000"
    echo "📚 Documentação da API: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo ""
    echo "Para parar o servidor: Ctrl+C"
    echo "=================================="

    python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    log_info "Servidor não iniciado. Para iniciar manualmente:"
    echo ""
    echo "  source venv/bin/activate"
    echo "  python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "Ou use o script de execução:"
    echo "  python3 scripts/run.py"
fi

log_success "Script de inicialização concluído!"