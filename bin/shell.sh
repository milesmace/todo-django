#!/bin/bash
#
# Open a shell in a Docker container
#
# Usage:
#   ./bin/shell.sh          # Opens bash in web container
#   ./bin/shell.sh web      # Opens bash in web container
#   ./bin/shell.sh celery   # Opens bash in celery container
#   ./bin/shell.sh db       # Opens psql in db container
#

set -e

SERVICE="${1:-api}"

case "$SERVICE" in
    db)
        echo "Connecting to PostgreSQL..."
        docker compose exec db psql -U postgres
        ;;
    cache|redis)
        echo "Connecting to Redis..."
        docker compose exec cache redis-cli
        ;;
    *)
        docker compose exec "$SERVICE" bash
        ;;
esac
