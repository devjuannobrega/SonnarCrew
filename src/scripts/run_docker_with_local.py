#!/usr/bin/env python3
"""
Script para executar container Docker conectando ao PostgreSQL local do Windows
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Executar comando e mostrar resultado"""
    print(f"\n{description}...")
    print(f"Executando: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Sucesso!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False


def check_docker():
    """Verificar Docker"""
    return run_command(["docker", "--version"], "Verificando Docker")


def build_image():
    """Build da imagem"""
    return run_command([
        "docker", "build",
        "-t", "code-analysis-agent:latest",
        "."
    ], "Fazendo build da imagem")


def test_postgres_connection():
    """Testar se PostgreSQL local está acessível"""
    print("\nTestando PostgreSQL local...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="251081",
            database="postgres"
        )
        conn.close()
        print("PostgreSQL local acessível!")
        return True
    except Exception as e:
        print(f"Erro conectando PostgreSQL local: {e}")
        return False


def run_container():
    """Executar container conectando ao PostgreSQL local"""

    # Para Windows, usar host.docker.internal para conectar ao host
    # Para Linux/Mac, usar host.docker.internal ou 172.17.0.1

    container_cmd = [
        "docker", "run",
        "--name", "code-analysis-app",
        "-p", "8000:8000",
        "--rm",  # Remove container quando parar
        "-e", "DATABASE_URL=postgresql+asyncpg://postgres:251081@host.docker.internal:5432/code_analysis_db",
        "-e", "DB_HOST=host.docker.internal",
        "-e", "DB_PORT=5432",
        "-e", "DB_USER=postgres",
        "-e", "DB_PASSWORD=251081",
        "-e", "DB_NAME=code_analysis_db",
        "-e", "ENVIRONMENT=production",
        "-e", "LOG_LEVEL=INFO",
        "-v", f"{Path.cwd()}/logs:/app/logs",  # Mapear logs
        "code-analysis-agent:latest"
    ]

    print("\nIniciando container...")
    print("Comando:", ' '.join(container_cmd))
    print("\nContainer será executado em primeiro plano.")
    print("Para parar: Ctrl+C")
    print("URL da API: http://localhost:8000")
    print("Documentação: http://localhost:8000/docs")

    try:
        # Executar em primeiro plano para ver logs
        subprocess.run(container_cmd, check=True)
    except KeyboardInterrupt:
        print("\nParando container...")
    except subprocess.CalledProcessError as e:
        print(f"Erro executando container: {e}")
        return False

    return True


def main():
    """Função principal"""
    print("EXECUTAR DOCKER COM POSTGRESQL LOCAL")
    print("=" * 50)

    # Verificar se estamos na raiz do projeto
    if not Path("main.py").exists():
        print("Execute este script na raiz do projeto!")
        sys.exit(1)

    # Verificar Docker
    if not check_docker():
        print("Docker não está funcionando!")
        sys.exit(1)

    # Testar PostgreSQL local
    if not test_postgres_connection():
        print("\nErro: PostgreSQL local não está acessível!")
        print("Verifique se:")
        print("1. PostgreSQL está rodando")
        print("2. Usuário 'postgres' existe")
        print("3. Senha é '251081'")
        print("4. Porta 5432 está aberta")
        sys.exit(1)

    # Menu
    print("\nOpções:")
    print("1. Build + Run (recomendado)")
    print("2. Apenas Build")
    print("3. Apenas Run (imagem já existe)")
    print("4. Run em background")

    try:
        choice = input("\nEscolha (1-4): ").strip()
    except KeyboardInterrupt:
        print("\nCancelado")
        sys.exit(0)

    if choice == "1":
        # Build + Run
        if build_image():
            run_container()

    elif choice == "2":
        # Apenas build
        build_image()

    elif choice == "3":
        # Apenas run
        run_container()

    elif choice == "4":
        # Run em background
        container_cmd = [
            "docker", "run",
            "-d",  # Background
            "--name", "code-analysis-app",
            "-p", "8000:8000",
            "-e", "DATABASE_URL=postgresql+asyncpg://postgres:251081@host.docker.internal:5432/code_analysis_db",
            "-e", "DB_HOST=host.docker.internal",
            "-e", "DB_PASSWORD=251081",
            "code-analysis-agent:latest"
        ]

        if run_command(container_cmd, "Executando container em background"):
            print("\nContainer rodando em background!")
            print("Logs: docker logs -f code-analysis-app")
            print("Parar: docker stop code-analysis-app")
            print("API: http://localhost:8000")

    else:
        print("Opção inválida")


if __name__ == "__main__":
    main()