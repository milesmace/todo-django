#!/bin/bash
#
# View logs from Docker containers
#
# Usage:
#   ./bin/logs.sh              # Follow all logs
#   ./bin/logs.sh web          # Follow web container logs
#   ./bin/logs.sh celery       # Follow celery container logs
#   ./bin/logs.sh --tail 100   # Show last 100 lines and follow
#

set -e

SERVICE=""
TAIL=""

for arg in "$@"; do
    case $arg in
        --tail|-n)
            shift
            TAIL="--tail $1"
            ;;
        -*)
            # Skip other flags
            ;;
        *)
            SERVICE="$arg"
            ;;
    esac
done

if [ -n "$SERVICE" ]; then
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f $TAIL "$SERVICE"
else
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f $TAIL
fi
