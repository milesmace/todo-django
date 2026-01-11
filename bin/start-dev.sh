#!/bin/bash
#
# Start the development environment
#
# Usage:
#   ./bin/start-dev.sh           # Start all services in background
#   ./bin/start-dev.sh --build   # Rebuild images before starting
#   ./bin/start-dev.sh --logs    # Start and follow logs
#

set -e

BUILD=""
LOGS=""

for arg in "$@"; do
    case $arg in
        --build|-b)
            BUILD="--build"
            ;;
        --logs|-l)
            LOGS="true"
            ;;
    esac
done

echo "Starting development environment..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d $BUILD

echo ""
echo "Services started:"
echo "  - Web:          http://localhost:8000"
echo "  - MailCatcher:  http://localhost:1081"
echo "  - RedisInsight: http://localhost:5540"
echo "  - PostgreSQL:   localhost:5432"
echo ""

if [ "$LOGS" = "true" ]; then
    echo "Following logs (Ctrl+C to stop)..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
fi
