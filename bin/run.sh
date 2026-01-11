#!/bin/bash
#
# Run Django management commands in the web container
#
# Usage:
#   ./bin/run.sh migrate
#   ./bin/run.sh makemigrations
#   ./bin/run.sh createsuperuser
#   ./bin/run.sh shell
#

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <manage.py command> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 migrate"
    echo "  $0 makemigrations"
    echo "  $0 createsuperuser"
    echo "  $0 shell"
    echo "  $0 collectstatic --noinput"
    exit 1
fi

docker compose exec web python src/manage.py "$@"
