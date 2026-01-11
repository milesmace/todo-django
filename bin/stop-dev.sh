#!/bin/bash
#
# Stop the development environment
#
# Usage:
#   ./bin/stop-dev.sh           # Stop all services
#   ./bin/stop-dev.sh --volumes # Stop and remove volumes (deletes data!)
#

set -e

VOLUMES=""

for arg in "$@"; do
    case $arg in
        --volumes|-v)
            VOLUMES="-v"
            echo "WARNING: This will delete all data (database, redis, etc.)!"
            read -p "Are you sure? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Aborted."
                exit 1
            fi
            ;;
    esac
done

echo "Stopping development environment..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml down $VOLUMES

echo "Development environment stopped."
