#!/usr/bin/env python3
"""
Script para build e gerenciamento de imagens Docker do Code Analysis Agent
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_command(command, description):
    """Executar comando e mostrar resultado"""
    print(f"\n{description}...")
    print(f"Executando: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Sucesso!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False


def check_docker():
    """Verificar se Docker está instalado e funcionando"""
    print("Verificando Docker...")

    if not run_command(["docker", "--version"], "Verificando versão do Docker"):
        print("Docker não está instalado ou não está funcionando")
        return False

    if not run_command(["docker", "ps"], "Verificando se Docker daemon está rodando"):
        print("Docker daemon não está rodando")
        return False

    return True


def build_image(image_name, tag="latest"):
    """Build da imagem Docker"""
    full_name = f"{image_name}:{tag}"

    print(f"\nBuild da imagem Docker: {full_name}")

    build_command = [
        "docker", "build",
        "-t", full_name,
        "."
    ]

    return run_command(build_command, f"Building imagem {full_name}")


def list_images(image_name):
    """Listar imagens criadas"""
    print(f"\nListando imagens {image_name}:")
    run_command(["docker", "images", image_name], "Listando imagens")


def run_image_test(image_name, tag="latest"):
    """Testar imagem criada"""
    full_name = f"{image_name}:{tag}"

    print(f"\nTestando imagem {full_name}...")

    test_command = [
        "docker", "run", "--rm",
        "-p", "8001:8000",
        "--name", "code-analysis-test",
        "-e", "DB_HOST=host.docker.internal",
        "-e", "DB_PASSWORD=251081",
        full_name
    ]

    print("Para testar a imagem, execute:")
    print(f"  {' '.join(test_command)}")
    print("Depois acesse: http://localhost:8001/health")
    print("Para parar: docker stop code-analysis-test")


def create_docker_compose_override():
    """Criar docker-compose.override.yml para desenvolvimento"""
    override_content = """version: '3.8'

services:
  api:
    image: code-analysis-agent:latest
    volumes:
      - .:/app
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:251081@postgres:5432/code_analysis_db
      - DB_PASSWORD=251081
    ports:
      - "8000:8000"
      - "5678:5678"
"""

    override_file = Path("docker-compose.override.yml")
    override_file.write_text(override_content)
    print(f"Arquivo {override_file} criado para desenvolvimento")


def run_docker_compose():
    """Rodar docker compose para subir toda a stack"""
    compose_file = "docker-compose.yml"

    if not Path(compose_file).exists():
        print(f"Arquivo {compose_file} não encontrado na raiz do projeto!")
        return False

    command = ["docker", "compose", "up", "-d", "--build"]
    return run_command(command, "Subindo stack completa com docker compose")


def main():
    """Função principal"""
    print("DOCKER BUILD - CODE ANALYSIS AGENT")
    print("=" * 50)

    if not Path("main.py").exists():
        print("Execute este script na raiz do projeto (onde está o main.py)")
        sys.exit(1)

    if not check_docker():
        sys.exit(1)

    image_name = "code-analysis-agent"

    # Menu de opções
    print("\nOpções disponíveis:")
    print("1. Build da imagem")
    print("2. Build com tag específica")
    print("3. Listar imagens")
    print("4. Testar imagem")
    print("5. Build + Teste")
    print("6. Criar docker-compose.override.yml")
    print("7. Build para produção")
    print("8. Subir stack completa com docker compose")

    try:
        choice = input("\nEscolha uma opção (1-8): ").strip()
    except KeyboardInterrupt:
        print("\nCancelado pelo usuário")
        sys.exit(0)

    if choice == "1":
        if build_image(image_name):
            list_images(image_name)
            print("\nImagem criada com sucesso!")
            print(f"Para testar: docker run -p 8000:8000 {image_name}")

    elif choice == "2":
        tag = input("Digite a tag (ex: v1.0, dev, prod): ").strip()
        if not tag:
            tag = "latest"

        if build_image(image_name, tag):
            list_images(image_name)
            print(f"\nImagem {image_name}:{tag} criada com sucesso!")

    elif choice == "3":
        list_images(image_name)

    elif choice == "4":
        tag = input("Digite a tag para testar (Enter para 'latest'): ").strip()
        if not tag:
            tag = "latest"
        run_image_test(image_name, tag)

    elif choice == "5":
        if build_image(image_name):
            list_images(image_name)
            run_image_test(image_name)
            print("\nBuild concluído e instruções de teste mostradas!")

    elif choice == "6":
        create_docker_compose_override()
        print("docker-compose.override.yml criado!")

    elif choice == "7":
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        prod_tag = f"prod-{timestamp}"

        print("Build para produção com múltiplas tags...")

        if build_image(image_name, "latest"):
            run_command(["docker", "tag", f"{image_name}:latest", f"{image_name}:{prod_tag}"],
                        f"Criando tag de produção {prod_tag}")
            run_command(["docker", "tag", f"{image_name}:latest", f"{image_name}:prod"],
                        "Criando tag prod")

            list_images(image_name)
            print(f"\nImagens de produção criadas:")
            print(f"  {image_name}:latest")
            print(f"  {image_name}:prod")
            print(f"  {image_name}:{prod_tag}")

    elif choice == "8":
        if run_docker_compose():
            print("\nStack completa iniciada com sucesso!")
            print("Acesse os serviços disponíveis:")
            print(" - API:      http://localhost:8000")
            print(" - Frontend: http://localhost:3000")
            print(" - PgAdmin:  http://localhost:8080")

    else:
        print("Opção inválida")
        sys.exit(1)


if __name__ == "__main__":
    main()

# #!/usr/bin/env python3
# """
# Script para build e gerenciamento de imagens Docker do Code Analysis Agent
# """
#
# import subprocess
# import sys
# import os
# from pathlib import Path
# from datetime import datetime
#
#
# def run_command(command, description):
#     """Executar comando e mostrar resultado"""
#     print(f"\n{description}...")
#     print(f"Executando: {' '.join(command)}")
#
#     try:
#         result = subprocess.run(command, check=True, capture_output=True, text=True)
#         print("Sucesso!")
#         if result.stdout:
#             print(f"Output: {result.stdout}")
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"Erro: {e}")
#         if e.stdout:
#             print(f"Stdout: {e.stdout}")
#         if e.stderr:
#             print(f"Stderr: {e.stderr}")
#         return False
#
#
# def check_docker():
#     """Verificar se Docker está instalado e funcionando"""
#     print("Verificando Docker...")
#
#     if not run_command(["docker", "--version"], "Verificando versão do Docker"):
#         print("Docker não está instalado ou não está funcionando")
#         return False
#
#     if not run_command(["docker", "ps"], "Verificando se Docker daemon está rodando"):
#         print("Docker daemon não está rodando")
#         return False
#
#     return True
#
#
# def build_image(image_name, tag="latest"):
#     """Build da imagem Docker"""
#     full_name = f"{image_name}:{tag}"
#
#     print(f"\nBuild da imagem Docker: {full_name}")
#
#     # Comando de build
#     build_command = [
#         "docker", "build",
#         "-t", full_name,
#         "."
#     ]
#
#     return run_command(build_command, f"Building imagem {full_name}")
#
#
# def list_images(image_name):
#     """Listar imagens criadas"""
#     print(f"\nListando imagens {image_name}:")
#     run_command(["docker", "images", image_name], "Listando imagens")
#
#
# def run_image_test(image_name, tag="latest"):
#     """Testar imagem criada"""
#     full_name = f"{image_name}:{tag}"
#
#     print(f"\nTestando imagem {full_name}...")
#
#     # Testar se a imagem inicia corretamente
#     test_command = [
#         "docker", "run", "--rm",
#         "-p", "8001:8000",  # Usar porta diferente para não conflitar
#         "--name", "code-analysis-test",
#         "-e", "DB_HOST=host.docker.internal",  # Para conectar ao PostgreSQL do host
#         "-e", "DB_PASSWORD=251081",
#         full_name
#     ]
#
#     print("Para testar a imagem, execute:")
#     print(f"  {' '.join(test_command)}")
#     print("Depois acesse: http://localhost:8001/health")
#     print("Para parar: docker stop code-analysis-test")
#
#
# def create_docker_compose_override():
#     """Criar docker-compose.override.yml para desenvolvimento"""
#     override_content = """version: '3.8'
#
# services:
#   api:
#     # Sobrescrever a imagem para usar a imagem local
#     image: code-analysis-agent:latest
#     # Mapear código local para desenvolvimento
#     volumes:
#       - .:/app
#       - ./logs:/app/logs
#     # Usar sua configuração local
#     environment:
#       - DATABASE_URL=postgresql+asyncpg://postgres:251081@postgres:5432/code_analysis_db
#       - DB_PASSWORD=251081
#     # Debugger port
#     ports:
#       - "8000:8000"
#       - "5678:5678"  # Para debug
# """
#
#     override_file = Path("docker-compose.override.yml")
#     override_file.write_text(override_content)
#     print(f"Arquivo {override_file} criado para desenvolvimento")
#
#
# def main():
#     """Função principal"""
#     print("DOCKER BUILD - CODE ANALYSIS AGENT")
#     print("=" * 50)
#
#     if not Path("main.py").exists():
#         print("Execute este script na raiz do projeto (onde está o main.py)")
#         sys.exit(1)
#
#     if not check_docker():
#         sys.exit(1)
#
#     image_name = "code-analysis-agent"
#
#     # Menu de opções
#     print("\nOpções disponíveis:")
#     print("1. Build da imagem")
#     print("2. Build com tag específica")
#     print("3. Listar imagens")
#     print("4. Testar imagem")
#     print("5. Build + Teste")
#     print("6. Criar docker-compose.override.yml")
#     print("7. Build para produção")
#
#     try:
#         choice = input("\nEscolha uma opção (1-7): ").strip()
#     except KeyboardInterrupt:
#         print("\nCancelado pelo usuário")
#         sys.exit(0)
#
#     if choice == "1":
#         # Build simples
#         if build_image(image_name):
#             list_images(image_name)
#             print("\nImagem criada com sucesso!")
#             print(f"Para testar: docker run -p 8000:8000 {image_name}")
#
#     elif choice == "2":
#         # Build com tag específica
#         tag = input("Digite a tag (ex: v1.0, dev, prod): ").strip()
#         if not tag:
#             tag = "latest"
#
#         if build_image(image_name, tag):
#             list_images(image_name)
#             print(f"\nImagem {image_name}:{tag} criada com sucesso!")
#
#     elif choice == "3":
#         # Listar imagens
#         list_images(image_name)
#
#     elif choice == "4":
#         # Testar imagem
#         tag = input("Digite a tag para testar (Enter para 'latest'): ").strip()
#         if not tag:
#             tag = "latest"
#         run_image_test(image_name, tag)
#
#     elif choice == "5":
#         if build_image(image_name):
#             list_images(image_name)
#             test_image(image_name)
#             print("\nBuild concluído e instruções de teste mostradas!")
#
#     elif choice == "6":
#         # Criar override
#         create_docker_compose_override()
#         print("docker-compose.override.yml criado!")
#
#     elif choice == "7":
#         # Build para produção
#         timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
#         prod_tag = f"prod-{timestamp}"
#
#         print("Build para produção com múltiplas tags...")
#
#         if build_image(image_name, "latest"):
#             run_command(["docker", "tag", f"{image_name}:latest", f"{image_name}:{prod_tag}"],
#                         f"Criando tag de produção {prod_tag}")
#             run_command(["docker", "tag", f"{image_name}:latest", f"{image_name}:prod"],
#                         "Criando tag prod")
#
#             list_images(image_name)
#             print(f"\nImagens de produção criadas:")
#             print(f"  {image_name}:latest")
#             print(f"  {image_name}:prod")
#             print(f"  {image_name}:{prod_tag}")
#
#     else:
#         print("Opção inválida")
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     main()