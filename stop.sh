#!/usr/bin/env bash
# Stops DataGatherer. The data (database and uploaded images) is kept.
set -euo pipefail
cd "$(dirname "$0")"
docker compose --env-file .env.docker down
printf '\nDataGatherer is stopped. Your data is kept; run ./start.sh to start it again.\n'
