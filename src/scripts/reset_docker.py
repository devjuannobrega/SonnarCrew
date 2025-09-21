#!/usr/bin/env python3
"""
Script para limpar e recriar containers Docker
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, ignore_errors=False):
    """Executar comando"""
    print(f"\n{description}...")
    print(f"Executando: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Sucesso!")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"Aviso: {e} (ignorado)")
            return True
        else:
            print(f"Erro: {e}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return False


def cleanup_containers():
    """Limpar containers existentes"""
    print("LIMPEZA DE CONTAINERS")
    print("=" * 30)

    containers = [
        "code_analysis_postgres",
        "code_analysis_redis",
        "code_analysis_api",
        "code_analysis_pgadmin",
        "hopeful_pasteur"  # Container que estava falhando
    ]

    for container in containers:
        run_command(["docker", "stop", container], f"Parando {container}", ignore_errors=True)
        run_command(["docker", "rm", container], f"Removendo {container}", ignore_errors=True)

    # Limpar volumes orfãos
    run_command(["docker", "volume", "prune", "-f"], "Limpando volumes órfãos", ignore_errors=True)

    # Limpar networks órfãs
    run_command(["docker", "network", "prune", "-f"], "Limpando networks órfãs", ignore_errors=True)

    return True


def remove_volumes():
    """Remover volumes para recriação completa"""
    print("\nREMOVENDO VOLUMES")
    print("=" * 20)

    volumes = [
        "sonnarcrew_postgres_data",
        "postgres_data",
        "sonnarcrew_redis_data",
        "redis_data",
        "sonnarcrew_pgadmin_data",
        "pgadmin_data"
    ]

    for volume in volumes:
        run_command(["docker", "volume", "rm", volume], f"Removendo volume {volume}", ignore_errors=True)

    return True


def test_docker_compose():
    """Testar arquivo docker-compose.yml"""
    print("\nTESTANDO DOCKER-COMPOSE")
    print("=" * 25)

    return run_command(["docker-compose", "config"], "Validando docker-compose.yml")


def rebuild_and_start():
    """Rebuild e iniciar serviços"""
    print("\nREBUILD E INICIALIZAÇÃO")
    print("=" * 25)

    # Parar tudo primeiro
    run_command(["docker-compose", "down", "-v"], "Parando docker-compose", ignore_errors=True)

    # Build das imagens
    if not run_command(["docker-compose", "build", "--no-cache"], "Fazendo build das imagens"):
        return False

    # Iniciar apenas PostgreSQL primeiro
    if not run_command(["docker-compose", "up", "-d", "postgres"], "Iniciando PostgreSQL"):
        return False

    print("\nAguardando PostgreSQL inicializar (30 segundos)...")
    import time
    time.sleep(30)

    # Verificar se PostgreSQL está funcionando
    if not run_command(["docker", "exec", "code_analysis_postgres", "pg_isready", "-U", "postgres"],
                       "Testando PostgreSQL"):
        print("PostgreSQL não está respondendo, mas continuando...")

    # Iniciar Redis
    if not run_command(["docker-compose", "up", "-d", "redis"], "Iniciando Redis"):
        return False

    # Aguardar mais um pouco
    time.sleep(10)

    # Iniciar API
    if not run_command(["docker-compose", "up", "-d", "api"], "Iniciando API"):
        return False

    print("\nTodos os serviços iniciados!")
    return True


def show_status():
    """Mostrar status dos containers"""
    print("\nSTATUS DOS CONTAINERS")
    print("=" * 25)

    run_command(["docker", "ps", "-a"], "Listando containers")
    run_command(["docker-compose", "ps"], "Status docker-compose")


def show_logs():
    """Mostrar logs recentes"""
    print("\nLOGS RECENTES")
    print("=" * 15)

    containers = ["postgres", "api", "redis"]
    for container in containers:
        print(f"\n--- Logs {container} ---")
        run_command(["docker-compose", "logs", "--tail=10", container], f"Logs {container}", ignore_errors=True)


def main():
    """Função principal"""
    print("RESET DOCKER - CODE ANALYSIS AGENT")
    print("=" * 40)

    if not Path("docker-compose.yml").exists():
        print("Arquivo docker-compose.yml não encontrado!")
        print("Execute este script na raiz do projeto")
        sys.exit(1)

    print("\nOpções:")
    print("1. Limpeza completa + Rebuild (recomendado)")
    print("2. Apenas limpeza de containers")
    print("3. Testar docker-compose.yml")
    print("4. Mostrar status atual")
    print("5. Mostrar logs")
    print("6. Limpeza + Rebuild sem volumes")

    try:
        choice = input("\nEscolha (1-6): ").strip()
    except KeyboardInterrupt:
        print("\nCancelado")
        sys.exit(0)

    if choice == "1":
        # Limpeza completa + rebuild
        cleanup_containers()
        remove_volumes()
        if test_docker_compose():
            rebuild_and_start()
            show_status()
            show_logs()

    elif choice == "2":
        # Apenas limpeza
        cleanup_containers()
        show_status()

    elif choice == "3":
        # Testar config
        test_docker_compose()

    elif choice == "4":
        # Status
        show_status()

    elif choice == "5":
        # Logs
        show_logs()

    elif choice == "6":
        # Limpeza sem volumes
        cleanup_containers()
        if test_docker_compose():
            rebuild_and_start()
            show_status()

    else:
        print("Opção inválida")
        sys.exit(1)


if __name__ == "__main__":
    main()