#!/usr/bin/env python3
"""
SonnarCrew - Code Analysis Agent
Docker Build & Management Script - Versão Otimizada

Autor: devjuannobrega
Versão: 2.0
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class BuildType(Enum):
    """Tipos de build disponíveis"""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    LATEST = "latest"


@dataclass
class Config:
    """Configuração do projeto"""
    project_name: str = "sonnarcrew"
    image_name: str = "code-analysis-agent"
    api_port: int = 8000
    frontend_port: int = 3000
    pgadmin_port: int = 8080
    debug_port: int = 5678
    db_name: str = "code_analysis_db"

    @property
    def db_password(self) -> str:
        """Obter senha do banco de dados de variável de ambiente"""
        return os.getenv('DB_PASSWORD', '251081')

    @property
    def database_url(self) -> str:
        """URL completa do banco de dados"""
        return f"postgresql+asyncpg://postgres:{self.db_password}@postgres:5432/{self.db_name}"


class Colors:
    """Cores para output do terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DockerManager:
    """Gerenciador de operações Docker"""

    def __init__(self, config: Config):
        self.config = config
        self.project_root = Path.cwd()

    def run_command(self, command: List[str], description: str, check: bool = True) -> Tuple[bool, str]:
        """Executar comando e retornar resultado"""
        print(f"\n{Colors.CYAN}🔧 {description}...{Colors.ENDC}")
        print(f"{Colors.BLUE}Executando: {' '.join(command)}{Colors.ENDC}")

        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Sucesso!{Colors.ENDC}")
                if result.stdout.strip():
                    print(f"{Colors.CYAN}Output:{Colors.ENDC} {result.stdout.strip()}")
                return True, result.stdout
            else:
                print(f"{Colors.RED}❌ Erro!{Colors.ENDC}")
                if result.stderr:
                    print(f"{Colors.RED}Stderr:{Colors.ENDC} {result.stderr}")
                return False, result.stderr

        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Erro: {e}{Colors.ENDC}")
            if e.stdout:
                print(f"{Colors.CYAN}Stdout:{Colors.ENDC} {e.stdout}")
            if e.stderr:
                print(f"{Colors.RED}Stderr:{Colors.ENDC} {e.stderr}")
            return False, str(e)
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Comando não encontrado: {command[0]}{Colors.ENDC}")
            return False, f"Comando não encontrado: {command[0]}"

    def check_prerequisites(self) -> bool:
        """Verificar pré-requisitos do sistema"""
        print(f"\n{Colors.HEADER}🔍 VERIFICANDO PRÉ-REQUISITOS{Colors.ENDC}")
        print("=" * 50)

        # Verificar se está na raiz do projeto
        required_files = ["main.py", "dockerfile", "docker-compose.yml"]
        missing_files = [f for f in required_files if not (self.project_root / f).exists()]

        if missing_files:
            print(f"{Colors.RED}❌ Arquivos obrigatórios não encontrados: {missing_files}{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Execute este script na raiz do projeto SonnarCrew{Colors.ENDC}")
            return False

        # Verificar Docker
        success, _ = self.run_command(["docker", "--version"], "Verificando Docker", check=False)
        if not success:
            print(f"{Colors.RED}❌ Docker não está instalado ou não está funcionando{Colors.ENDC}")
            return False

        success, _ = self.run_command(["docker", "ps"], "Verificando Docker daemon", check=False)
        if not success:
            print(f"{Colors.RED}❌ Docker daemon não está rodando{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Inicie o Docker Desktop ou Docker service{Colors.ENDC}")
            return False

        # Verificar Docker Compose
        success, _ = self.run_command(["docker", "compose", "version"], "Verificando Docker Compose", check=False)
        if not success:
            print(f"{Colors.YELLOW}⚠️  Docker Compose não encontrado, tentando versão legacy{Colors.ENDC}")
            success, _ = self.run_command(["docker-compose", "--version"], "Verificando docker-compose", check=False)
            if not success:
                print(f"{Colors.RED}❌ Docker Compose não está disponível{Colors.ENDC}")
                return False

        print(f"\n{Colors.GREEN}✅ Todos os pré-requisitos verificados com sucesso!{Colors.ENDC}")
        return True

    def build_image(self, build_type: BuildType = BuildType.LATEST, custom_tag: Optional[str] = None) -> bool:
        """Build da imagem Docker"""
        if custom_tag:
            tag = custom_tag
        else:
            if build_type == BuildType.PRODUCTION:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                tag = f"prod-{timestamp}"
            else:
                tag = build_type.value

        full_name = f"{self.config.image_name}:{tag}"

        print(f"\n{Colors.HEADER}🔨 BUILD DA IMAGEM DOCKER{Colors.ENDC}")
        print(f"{Colors.CYAN}Imagem: {full_name}{Colors.ENDC}")
        print(f"{Colors.CYAN}Tipo: {build_type.name}{Colors.ENDC}")

        # Verificar se Dockerfile existe
        dockerfile_path = self.project_root / "dockerfile"
        if not dockerfile_path.exists():
            print(f"{Colors.RED}❌ Dockerfile não encontrado em: {dockerfile_path}{Colors.ENDC}")
            return False

        build_command = [
            "docker", "build",
            "-t", full_name,
            "--build-arg", f"BUILD_TYPE={build_type.value}",
            "."
        ]

        success, _ = self.run_command(build_command, f"Building imagem {full_name}")

        if success and build_type == BuildType.PRODUCTION:
            # Criar tags adicionais para produção
            self.run_command(
                ["docker", "tag", full_name, f"{self.config.image_name}:prod"],
                "Criando tag prod"
            )
            self.run_command(
                ["docker", "tag", full_name, f"{self.config.image_name}:latest"],
                "Atualizando tag latest"
            )

        return success

    def list_images(self) -> bool:
        """Listar imagens do projeto"""
        print(f"\n{Colors.HEADER}📋 IMAGENS DISPONÍVEIS{Colors.ENDC}")
        return self.run_command(
            ["docker", "images", self.config.image_name],
            "Listando imagens do projeto"
        )[0]

    def create_test_command(self, tag: str = "latest") -> str:
        """Criar comando de teste para a imagem"""
        full_name = f"{self.config.image_name}:{tag}"

        test_command = [
            "docker", "run", "--rm",
            "-p", f"{self.config.api_port + 1}:{self.config.api_port}",
            "--name", f"{self.config.project_name}-test",
            "-e", "DB_HOST=host.docker.internal",
            "-e", f"DB_PASSWORD={self.config.db_password}",
            "-e", "ENVIRONMENT=test",
            full_name
        ]

        return " ".join(test_command)

    def show_test_instructions(self, tag: str = "latest") -> None:
        """Mostrar instruções de teste"""
        print(f"\n{Colors.HEADER}🧪 INSTRUÇÕES DE TESTE{Colors.ENDC}")
        print("=" * 50)

        test_cmd = self.create_test_command(tag)

        print(f"{Colors.CYAN}Para testar a imagem, execute:{Colors.ENDC}")
        print(f"{Colors.GREEN}{test_cmd}{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Depois acesse:{Colors.ENDC}")
        print(f"  📊 Health Check: http://localhost:{self.config.api_port + 1}/health")
        print(f"  📖 Docs API:     http://localhost:{self.config.api_port + 1}/docs")
        print(f"\n{Colors.CYAN}Para parar:{Colors.ENDC}")
        print(f"  docker stop {self.config.project_name}-test")

    def create_docker_compose_override(self) -> bool:
        """Criar docker-compose.override.yml para desenvolvimento"""
        override_content = f"""version: '3.8'

services:
  api:
    image: {self.config.image_name}:latest
    build: .
    volumes:
      - .:/app
      - ./logs:/app/logs
      - /app/venv  # Preservar virtual environment
    environment:
      - DATABASE_URL={self.config.database_url}
      - DB_PASSWORD={self.config.db_password}
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "{self.config.api_port}:{self.config.api_port}"
      - "{self.config.debug_port}:{self.config.debug_port}"  # Debug port
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true

  postgres:
    environment:
      - POSTGRES_PASSWORD={self.config.db_password}
      - POSTGRES_DB={self.config.db_name}
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"  # Expor porta para desenvolvimento

volumes:
  postgres_dev_data:
"""

        override_file = self.project_root / "docker-compose.override.yml"
        try:
            override_file.write_text(override_content)
            print(f"{Colors.GREEN}✅ Arquivo {override_file.name} criado para desenvolvimento{Colors.ENDC}")
            print(f"{Colors.CYAN}💡 Use 'docker compose up -d' para subir o ambiente de desenvolvimento{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao criar override: {e}{Colors.ENDC}")
            return False

    def run_docker_compose(self, build: bool = True, detached: bool = True) -> bool:
        """Executar docker compose"""
        compose_file = self.project_root / "docker-compose.yml"

        if not compose_file.exists():
            print(f"{Colors.RED}❌ Arquivo docker-compose.yml não encontrado!{Colors.ENDC}")
            return False

        command = ["docker", "compose", "up"]
        if detached:
            command.append("-d")
        if build:
            command.append("--build")

        success, _ = self.run_command(command, "Subindo stack completa")

        if success:
            print(f"\n{Colors.GREEN}🚀 STACK INICIADA COM SUCESSO!{Colors.ENDC}")
            print("=" * 50)
            print(f"{Colors.CYAN}Serviços disponíveis:{Colors.ENDC}")
            print(f"  🔧 API:      http://localhost:{self.config.api_port}")
            print(f"  🌐 Frontend: http://localhost:{self.config.frontend_port}")
            print(f"  🗄️  PgAdmin:  http://localhost:{self.config.pgadmin_port}")
            print(f"\n{Colors.CYAN}Comandos úteis:{Colors.ENDC}")
            print(f"  📊 Status:   docker compose ps")
            print(f"  📋 Logs:     docker compose logs -f")
            print(f"  ⏹️  Parar:    docker compose down")

        return success

    def cleanup_images(self) -> bool:
        """Limpar imagens antigas"""
        print(f"\n{Colors.HEADER}🧹 LIMPEZA DE IMAGENS{Colors.ENDC}")

        # Listar imagens dangling
        success, output = self.run_command(
            ["docker", "images", "-f", "dangling=true", "-q"],
            "Procurando imagens órfãs",
            check=False
        )

        if success and output.strip():
            clean_success, _ = self.run_command(
                ["docker", "rmi"] + output.strip().split('\n'),
                "Removendo imagens órfãs"
            )
            return clean_success
        else:
            print(f"{Colors.GREEN}✅ Nenhuma imagem órfã encontrada{Colors.ENDC}")
            return True

    def show_status(self) -> None:
        """Mostrar status dos containers"""
        print(f"\n{Colors.HEADER}📊 STATUS DOS CONTAINERS{Colors.ENDC}")
        self.run_command(["docker", "compose", "ps"], "Status dos serviços")

        print(f"\n{Colors.HEADER}💾 USO DE ESPAÇO{Colors.ENDC}")
        self.run_command(["docker", "system", "df"], "Uso de espaço Docker")


def show_banner() -> None:
    """Mostrar banner do aplicativo"""
    banner = f"""{Colors.HEADER}
╔═══════════════════════════════════════════════════════════╗
║                      🚀 SONNARCREW 🚀                    ║
║                Code Analysis Agent - Docker Manager       ║
║                                                           ║
║                   Versão 2.0 - Otimizada                 ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)


def show_menu() -> None:
    """Mostrar menu de opções"""
    print(f"\n{Colors.HEADER}📋 OPÇÕES DISPONÍVEIS{Colors.ENDC}")
    print("=" * 50)
    print(f"{Colors.CYAN}🔨 BUILD & DESENVOLVIMENTO{Colors.ENDC}")
    print("  1. Build da imagem (latest)")
    print("  2. Build com tag específica")
    print("  3. Build para desenvolvimento")
    print("  4. Build para produção")
    print()
    print(f"{Colors.CYAN}🧪 TESTE & VALIDAÇÃO{Colors.ENDC}")
    print("  5. Testar imagem")
    print("  6. Build + Teste completo")
    print()
    print(f"{Colors.CYAN}📋 GERENCIAMENTO{Colors.ENDC}")
    print("  7. Listar imagens")
    print("  8. Status dos containers")
    print("  9. Limpar imagens antigas")
    print()
    print(f"{Colors.CYAN}🚀 DEPLOY & AMBIENTE{Colors.ENDC}")
    print("  10. Criar ambiente de desenvolvimento")
    print("  11. Subir stack completa")
    print("  12. Parar todos os containers")
    print()
    print(f"{Colors.CYAN}🔧 UTILITÁRIOS{Colors.ENDC}")
    print("  13. Gerar docker-compose.override.yml")
    print("  14. Verificar pré-requisitos")
    print("  0.  Sair")


def get_user_choice() -> str:
    """Obter escolha do usuário"""
    try:
        choice = input(f"\n{Colors.YELLOW}Escolha uma opção (0-14): {Colors.ENDC}").strip()
        return choice
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Cancelado pelo usuário{Colors.ENDC}")
        sys.exit(0)


def main() -> None:
    """Função principal"""
    show_banner()

    config = Config()
    docker_manager = DockerManager(config)

    if not docker_manager.check_prerequisites():
        sys.exit(1)

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "0":
            print(f"{Colors.GREEN}👋 Até logo!{Colors.ENDC}")
            break

        elif choice == "1":
            if docker_manager.build_image(BuildType.LATEST):
                docker_manager.list_images()
                docker_manager.show_test_instructions()

        elif choice == "2":
            tag = input(f"{Colors.CYAN}Digite a tag (ex: v1.0, dev, staging): {Colors.ENDC}").strip()
            if not tag:
                tag = "latest"
            if docker_manager.build_image(BuildType.LATEST, tag):
                docker_manager.list_images()
                docker_manager.show_test_instructions(tag)

        elif choice == "3":
            if docker_manager.build_image(BuildType.DEVELOPMENT):
                docker_manager.list_images()
                docker_manager.show_test_instructions("dev")

        elif choice == "4":
            if docker_manager.build_image(BuildType.PRODUCTION):
                docker_manager.list_images()
                print(f"{Colors.GREEN}🎉 Build de produção concluído com sucesso!{Colors.ENDC}")

        elif choice == "5":
            tag = input(f"{Colors.CYAN}Digite a tag para testar (Enter para 'latest'): {Colors.ENDC}").strip()
            if not tag:
                tag = "latest"
            docker_manager.show_test_instructions(tag)

        elif choice == "6":
            if docker_manager.build_image(BuildType.LATEST):
                docker_manager.list_images()
                docker_manager.show_test_instructions()
                print(f"{Colors.GREEN}🎉 Build e teste configurados com sucesso!{Colors.ENDC}")

        elif choice == "7":
            docker_manager.list_images()

        elif choice == "8":
            docker_manager.show_status()

        elif choice == "9":
            docker_manager.cleanup_images()

        elif choice == "10":
            docker_manager.create_docker_compose_override()

        elif choice == "11":
            docker_manager.run_docker_compose()

        elif choice == "12":
            docker_manager.run_command(
                ["docker", "compose", "down"],
                "Parando todos os containers"
            )

        elif choice == "13":
            docker_manager.create_docker_compose_override()

        elif choice == "14":
            docker_manager.check_prerequisites()

        else:
            print(f"{Colors.RED}❌ Opção inválida!{Colors.ENDC}")

        if choice != "0":
            input(f"\n{Colors.CYAN}Pressione Enter para continuar...{Colors.ENDC}")


if __name__ == "__main__":
    main()

# #!/usr/bin/env python3
# """
# Script para build e gerenciamento de imagens Docker do Code Analysis Agent
# """
#
# import subprocess
# import sys
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
#     test_command = [
#         "docker", "run", "--rm",
#         "-p", "8001:8000",
#         "--name", "code-analysis-test",
#         "-e", "DB_HOST=host.docker.internal",
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
#     image: code-analysis-agent:latest
#     volumes:
#       - .:/app
#       - ./logs:/app/logs
#     environment:
#       - DATABASE_URL=postgresql+asyncpg://postgres:251081@postgres:5432/code_analysis_db
#       - DB_PASSWORD=251081
#     ports:
#       - "8000:8000"
#       - "5678:5678"
# """
#
#     override_file = Path("docker-compose.override.yml")
#     override_file.write_text(override_content)
#     print(f"Arquivo {override_file} criado para desenvolvimento")
#
#
# def run_docker_compose():
#     """Rodar docker compose para subir toda a stack"""
#     compose_file = "docker-compose.yml"
#
#     if not Path(compose_file).exists():
#         print(f"Arquivo {compose_file} não encontrado na raiz do projeto!")
#         return False
#
#     command = ["docker", "compose", "up", "-d", "--build"]
#     return run_command(command, "Subindo stack completa com docker compose")
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
#     print("8. Subir stack completa com docker compose")
#
#     try:
#         choice = input("\nEscolha uma opção (1-8): ").strip()
#     except KeyboardInterrupt:
#         print("\nCancelado pelo usuário")
#         sys.exit(0)
#
#     if choice == "1":
#         if build_image(image_name):
#             list_images(image_name)
#             print("\nImagem criada com sucesso!")
#             print(f"Para testar: docker run -p 8000:8000 {image_name}")
#
#     elif choice == "2":
#         tag = input("Digite a tag (ex: v1.0, dev, prod): ").strip()
#         if not tag:
#             tag = "latest"
#
#         if build_image(image_name, tag):
#             list_images(image_name)
#             print(f"\nImagem {image_name}:{tag} criada com sucesso!")
#
#     elif choice == "3":
#         list_images(image_name)
#
#     elif choice == "4":
#         tag = input("Digite a tag para testar (Enter para 'latest'): ").strip()
#         if not tag:
#             tag = "latest"
#         run_image_test(image_name, tag)
#
#     elif choice == "5":
#         if build_image(image_name):
#             list_images(image_name)
#             run_image_test(image_name)
#             print("\nBuild concluído e instruções de teste mostradas!")
#
#     elif choice == "6":
#         create_docker_compose_override()
#         print("docker-compose.override.yml criado!")
#
#     elif choice == "7":
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
#     elif choice == "8":
#         if run_docker_compose():
#             print("\nStack completa iniciada com sucesso!")
#             print("Acesse os serviços disponíveis:")
#             print(" - API:      http://localhost:8000")
#             print(" - Frontend: http://localhost:3000")
#             print(" - PgAdmin:  http://localhost:8080")
#
#     else:
#         print("Opção inválida")
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     main()