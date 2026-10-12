#!/usr/bin/env bash
# Starts DataGatherer and opens it in the browser. Only Docker Desktop is needed.
# On the first start it creates .env.docker with random passwords and picks a free port.
# Usage: ./start.sh [--no-browser]
set -euo pipefail
cd "$(dirname "$0")"

ENV_FILE=.env.docker
OPEN_BROWSER=1
[ "${1:-}" = "--no-browser" ] && OPEN_BROWSER=0

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
fail() { printf '\n\033[31mERROR:\033[0m %s\n\n' "$1" >&2; exit 1; }

# Random hexadecimal string with $1 bytes of entropy
random_hex() { od -An -tx1 -N"$1" /dev/urandom | tr -d ' \n'; }

# True when a program already listens on 127.0.0.1:$1
port_in_use() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

env_value() { grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d "'\"" || true; }

compose() { docker compose --env-file "$ENV_FILE" "$@"; }

# Everything runs inside main, called on the last line: bash reads a script while running it, so without
# this an update of this file during a start (e.g. while images download) would make bash read garbage.
main() {
    step "Checking Docker"
    command -v docker >/dev/null 2>&1 \
        || fail "Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/ , start it, then run this again."
    docker info >/dev/null 2>&1 \
        || fail "Docker is installed but not running. Open Docker Desktop, wait until it shows \"Engine running\", then run this again."
    docker compose version >/dev/null 2>&1 \
        || fail "This Docker version has no 'docker compose'. Update Docker Desktop, then run this again."


    first_start=0
    if [ ! -f "$ENV_FILE" ]; then
        step "First start: creating the configuration with new random passwords"
        [ -f .env.docker.example ] || fail ".env.docker.example is missing. Download DataGatherer again, then run this again."
        db_password=$(random_hex 24)
        # Written to a temporary file first, so a failure never leaves a half-written configuration behind
        sed -e "s/^SECRET_KEY=change-me$/SECRET_KEY=$(random_hex 40)/" \
            -e "s/^SQL_PASSWORD=change-me$/SQL_PASSWORD=$db_password/" \
            -e "s/^POSTGRES_PASSWORD=change-me$/POSTGRES_PASSWORD=$db_password/" \
            -e "s/^DJANGO_SUPERUSER_PASSWORD=change-me$/DJANGO_SUPERUSER_PASSWORD=$(random_hex 12)/" \
            .env.docker.example > "$ENV_FILE.tmp"
        mv "$ENV_FILE.tmp" "$ENV_FILE"
        first_start=1
    fi
    if grep -q '=change-me$' "$ENV_FILE"; then
        fail "$ENV_FILE still contains 'change-me' values. Replace each of them with a long random value, then run this again."
    fi


    already_running=$(compose ps --status running --services 2>/dev/null | grep -c '^nginx$' || true)
    port=$(env_value APP_PORT)
    if [ -z "$port" ]; then
        port=8080
        while port_in_use "$port"; do
            port=$((port + 1))
            [ "$port" -le 8099 ] || fail "Ports 8080 to 8099 are all in use. Set APP_PORT to a free port in $ENV_FILE, then run this again."
        done
        printf '\n# Port of the app on this computer, chosen at the first start\nAPP_PORT=%s\n' "$port" >> "$ENV_FILE"
    elif [ "$already_running" = 0 ] && port_in_use "$port"; then
        fail "Port $port is used by another program. Close that program, or set APP_PORT to another port in $ENV_FILE, then run this again."
    fi
    url="http://127.0.0.1:$port"
    pre_path=$(env_value PRE_PATH)


    step "Downloading DataGatherer (the first time takes a few minutes)"
    if ! compose pull --quiet; then
        step "Download not possible: building DataGatherer on this computer instead (10 to 20 minutes)"
        compose build
    fi

    step "Starting DataGatherer"
    compose up -d


    step "Waiting for DataGatherer to be ready"
    ready=0
    for _ in $(seq 1 150); do
        if curl -fsS -o /dev/null "$url/${pre_path}a/admin/login/" 2>/dev/null; then
            ready=1
            break
        fi
        sleep 2
    done
    if [ "$ready" = 0 ]; then
        compose logs --tail 40 django
        fail "DataGatherer did not start. The messages above say why; send them to whoever maintains the app."
    fi


    step "DataGatherer is running at $url"
    if [ "$first_start" = 1 ]; then
        printf 'Administrator account (also saved in %s):\n  user:      %s\n  password:  %s\n' \
            "$ENV_FILE" "$(env_value DJANGO_SUPERUSER_USERNAME)" "$(env_value DJANGO_SUPERUSER_PASSWORD)"
    else
        printf 'Log in with your account. The administrator password chosen at the first start is\nDJANGO_SUPERUSER_PASSWORD in %s.\n' "$ENV_FILE"
    fi
    printf 'Create accounts for other people at %s/%sa/admin/\n' "$url" "$pre_path"
    printf 'To stop DataGatherer run ./stop.sh (double-click "stop.command" on a Mac). Your data is kept.\n'

    if [ "$OPEN_BROWSER" = 1 ]; then
        if command -v open >/dev/null 2>&1; then
            open "$url"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$url" >/dev/null 2>&1 || true
        fi
    fi
}

main "$@"; exit
