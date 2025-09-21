#!/bin/bash

# Script para aguardar o banco de dados estar disponível
# Usado no Docker container antes de iniciar a aplicação

set -e

# Variáveis de ambiente com valores padrão
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-password}
DB_NAME=${DB_NAME:-code_analysis_db}

# Timeout em segundos
TIMEOUT=${DB_TIMEOUT:-60}

echo "Aguardando PostgreSQL estar disponível..."
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "Database: $DB_NAME"

# Função para testar conexão
test_connection() {
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1" > /dev/null 2>&1
}

# Aguardar PostgreSQL
counter=0
while ! test_connection; do
    counter=$((counter + 1))
    if [ $counter -gt $TIMEOUT ]; then
        echo "ERRO: Timeout aguardando PostgreSQL ($TIMEOUT segundos)"
        echo "Verifique se PostgreSQL está rodando em $DB_HOST:$DB_PORT"
        exit 1
    fi

    echo "PostgreSQL não disponível ainda... tentativa $counter/$TIMEOUT"
    sleep 1
done

echo "PostgreSQL está disponível!"

# Verificar se database existe, se não, criar
echo "Verificando se database '$DB_NAME' existe..."
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Criando database '$DB_NAME'..."
    PGPASSWORD=$DB_PASSWORD createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    echo "Database criado!"
else
    echo "Database '$DB_NAME' já existe"
fi

echo "Sistema pronto para iniciar!"
echo "Executando: $@"

# Executar comando passado como parâmetro
exec "$@"