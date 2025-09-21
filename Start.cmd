@echo off
REM ===============================================================================
REM SonnarCrew - Simple Launcher
REM Executa o build_docker.py com as cores bonitas
REM ===============================================================================

setlocal EnableDelayedExpansion

REM Verificar se está na raiz do projeto
if not exist "main.py" (
    echo ERRO: Execute este script na raiz do projeto SonnarCrew
    echo Arquivos encontrados:
    dir /b
    pause
    exit /b 1
)

if not exist "build_docker.py" (
    echo ERRO: build_docker.py nao encontrado!
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Python nao encontrado!
        echo Instale Python 3.8+ e adicione ao PATH
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker nao encontrado!
    echo Instale Docker Desktop e inicie o servico
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker daemon nao esta rodando!
    echo Inicie Docker Desktop e tente novamente
    pause
    exit /b 1
)

REM Ativar virtual environment se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Executar o script Python com cores bonitas
%PYTHON_CMD% build_docker.py

REM Manter janela aberta se houver erro
if %errorlevel% neq 0 (
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
)

exit /b %errorlevel%