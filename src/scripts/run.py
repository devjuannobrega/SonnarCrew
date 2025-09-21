#!/usr/bin/env python3
"""
Development runner script - VERSÃO CORRIGIDA para encontrar .env
"""

import asyncio
import os
import sys
import uvicorn
from pathlib import Path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
expected_files = ["main.py", "requirements.txt", ".env", "docker-compose.yml"]
found_indicators = [f for f in expected_files if (project_root / f).exists()]

if not found_indicators:
    possible_roots = [
        current_file.parent.parent.parent,
        current_file.parent.parent,
        Path.cwd(),
    ]

    for possible_root in possible_roots:
        found = [f for f in expected_files if (possible_root / f).exists()]
        if found:
            project_root = possible_root
            break

sys.path.insert(0, str(project_root))

print(f"📁 Diretório atual do script: {current_file.parent}")
print(f"📁 Raiz do projeto detectada: {project_root}")


def load_env_variables():
    """Carregar variáveis de ambiente do arquivo .env"""
    env_file = project_root / ".env"
    print(f"🔍 Procurando arquivo .env em: {env_file}")
    if env_file.exists():
        print("✅ Arquivo .env encontrado!")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)

            db_host = os.getenv("DB_HOST")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME")

            print("📋 Configurações carregadas:")
            print(f"   DB_HOST: {db_host}")
            print(f"   DB_USER: {db_user}")
            print(f"   DB_PASSWORD: {'*' * len(db_password) if db_password else 'NÃO DEFINIDA'}")
            print(f"   DB_NAME: {db_name}")

            return True

        except ImportError:
            print("❌ python-dotenv não instalado!")
            print("   Execute: pip install python-dotenv")
            return False

    else:
        print("❌ Arquivo .env NÃO encontrado!")
        print(f"   Esperado em: {env_file}")

        # Listar arquivos na raiz para debug
        print("📂 Arquivos na raiz do projeto:")
        for item in project_root.iterdir():
            if item.is_file():
                print(f"   {item.name}")

        return False


async def check_database():
    """Check if database is accessible and create tables if needed"""
    try:
        from src.database.database import create_tables
        await create_tables()
        print("✅ Database tables created/verified successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")

        # Verificar se é problema de conexão específico
        if "connection was closed" in str(e):
            print("\n🔧 Problema de conexão detectado:")
            print("   1. PostgreSQL não está rodando")
            print("   2. Credenciais incorretas")
            print("   3. Firewall bloqueando porta 5432")

        return False


async def test_basic_functionality():
    """Test basic agent functionality"""
    try:
        from src.agents.code_analyzer_agent import CodeAnalyzerAgent

        agent = CodeAnalyzerAgent()
        test_code = """
def hello():
    print("Hello, World!")
"""

        result = await agent.analyze_code(test_code)
        print("✅ Code analysis agent working correctly")
        print(f"   Found {len(result.get('suggestions', []))} suggestions")
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


async def test_yaml_config():
    """Test YAML configuration loading"""
    try:
        from src.tools.crew import CrewTool

        crew_tool = CrewTool()
        agents_config = crew_tool.load_agents_config()
        tasks_config = crew_tool.load_tasks_config()

        agents_count = len(agents_config.get("agents", {}))
        tasks_count = len(tasks_config.get("tasks", {}))

        if agents_count > 0 and tasks_count > 0:
            print(f"✅ YAML configurations loaded ({agents_count} agents, {tasks_count} tasks)")
            return True
        else:
            print("⚠️  YAML configurations using defaults")
            return True  # Não é crítico

    except Exception as e:
        print(f"❌ YAML config test failed: {e}")
        return True  # Não é crítico


async def main():
    """Main runner function"""
    print("🚀 Starting Code Analysis Agent Development Server")
    print("=" * 60)

    # PRIMEIRO: Carregar variáveis de ambiente
    print("\n🔧 Carregando configurações...")
    env_loaded = load_env_variables()

    if not env_loaded:
        print("\n❌ Não foi possível carregar o arquivo .env")
        print("Verifique se o arquivo existe na raiz do projeto")

        # Perguntar se deve continuar
        try:
            response = input("\nContinuar mesmo assim? (y/n): ").lower()
            if response != 'y':
                print("👋 Saindo...")
                return
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            return

    # Test YAML configuration
    print("\n🔧 Verificando configurações YAML...")
    yaml_ok = await test_yaml_config()

    # Test database connectivity
    print("\n📊 Verificando conectividade com banco...")
    db_ok = await check_database()

    # Test agent functionality
    print("\n🤖 Testando funcionalidade do agente...")
    agent_ok = await test_basic_functionality()

    # Avaliar resultados
    critical_issues = []
    if not agent_ok:
        critical_issues.append("Agente de análise")

    if critical_issues:
        print(f"\n❌ Problemas críticos encontrados: {', '.join(critical_issues)}")
        return

    if not db_ok:
        print("\n⚠️  Banco de dados não disponível - algumas funcionalidades não funcionarão")
        print("Para resolver:")
        print("1. Instalar PostgreSQL: https://www.postgresql.org/download/")
        print("2. Ou usar Docker: docker run -d --name postgres -e POSTGRES_PASSWORD=251081 -p 5432:5432 postgres")
        print("3. Ou usar modo standalone: python scripts/run_standalone.py")

        try:
            response = input("\nContinuar mesmo assim? (y/n): ").lower()
            if response != 'y':
                print("👋 Use: python scripts/run_standalone.py para versão sem banco")
                return
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            return

    print("\n✅ Sistema pronto para iniciar!")
    print("\n📡 Iniciando servidor FastAPI...")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print("   Config Info: http://localhost:8000/config-info")
    print("   Para parar: Ctrl+C")
    print("=" * 60)

    # Mudar para diretório raiz antes de iniciar uvicorn
    os.chdir(project_root)

    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor parado")


if __name__ == "__main__":
    asyncio.run(main())