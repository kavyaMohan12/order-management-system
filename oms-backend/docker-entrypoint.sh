#!/bin/sh
set -e
alembic upgrade head
python -m app.scripts.seed_products
exec "$@"
