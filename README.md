# DataGatherer

Semi‑automatic structured data extraction from image collections

## Overview

DataGatherer is a full‑stack application that assists in turning sets of images into structured, queryable information. It provides tooling to upload, organize, derive relationships, and finally generate a user–hashtag matrix showing how frequently users have used specific tags. The goal: accelerate manual curation while preserving accuracy.

## Key Features

- Semi‑automatic data extraction workflow from uploaded images
- User ↔ hashtag frequency matrix generation
- OCR & suggestion services (extensible service layer)
- Django admin for direct entity management
- Index computation & similarity (Annoy index present in repo)
- Containerized deployment (Docker + docker compose)
- Reverse‑proxied via Nginx (scalable edge layer)

## Architecture

```
┌────────────┐    ┌──────────────┐    ┌──────────────┐
│   React    │ →  │   Django API │ →  │  Services /  │
│ Frontend   │    │  (job/storage│    │  Compute/Idx │
└────────────┘    │  functions)  │    └──────────────┘
				│          │        │                │
				▼          ▼        ▼                ▼
		 Nginx ← docker network / persistence / media volume
```

Core backend apps:
- `functions_api` – common functions & business logic
- `job_api` – job orchestration & processing logic
- `storage_api` – models/serialization for stored entities
- `services` – OCR, suggestion & index computation modules

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React (JS) |
| Backend    | Django     |
| Services   | Python modules (OCR / Annoy) |
| Proxy      | Nginx      |
| Packaging  | Docker / docker compose |
| Data Store | (Likely Django default DB / configure externally) |

## Data Output (Example Matrix)

|           | user_1    | user_2 | ... | user_3    |
|-----------|-----------|--------|-----|-----------|
| hashtag_1 | weight_11 |        |     |           |
| hashtag_2 |           |        |     |           |
| hashtag_n |           |        |     | weight_nn |

Definition: <code>weight(user, hashtag)</code> = number of posts by that user containing the hashtag.

## Security & Precautions

This application is designed for **local use only**.

Please ensure:
1. The app is only reachable from the computer it runs on (the port is published on `127.0.0.1`). Do not change that without HTTPS and a firewall.
2. Every secret in `.env.docker` is unique and random (it is git‑ignored; never commit it).
3. If the site is ever served over HTTPS, set `SECURE_COOKIES=1` in `.env.docker`.

What the application enforces:
- Login tokens are kept in `HttpOnly`, `SameSite=Strict` cookies that page scripts cannot read; cookie‑authenticated writes require the CSRF token. Logging out revokes the refresh token.
- After 5 failed logins (API or admin) a username is locked for 15 minutes from that IP address (`LOGIN_FAILURE_LIMIT`, `LOGIN_LOCKOUT_MINUTES`). Unlock earlier with `python manage.py axes_reset_username <username>`.
- Uploaded images are only served to their owner (and to staff); nginx sends the file once Django has authorized the request.
- Each user only sees and changes their own projects and data.
- The app calls its API on the same address it is opened on, so the login cookies never leave that address.

## Getting Started (no technical knowledge needed)

You only need **Docker Desktop**: download it from <https://www.docker.com/products/docker-desktop/>, install it and open it once.

1. Download DataGatherer: on GitHub press **Code → Download ZIP** and unzip it (or `git clone` it).
2. Start it:
   - **Mac**: double-click `start.command` (the first time: right-click → *Open*, then confirm).
   - **Windows**: double-click `start.bat`.
   - **Linux**: run `./start.sh` in a terminal.
3. Wait. The first start downloads DataGatherer (about 800 MB: a few minutes, depending on your connection); later starts take seconds.
   When it is ready, the app opens in your browser and the window shows the **administrator user and password**.
   Keep them: they are also saved in the file `.env.docker`.

To stop DataGatherer double-click `stop.command` (Mac) or `stop.bat` (Windows), or run `./stop.sh`. Your projects and images are kept, also when the computer restarts.

To give other people access, open the admin page shown at the end of the start (e.g. `http://127.0.0.1:8080/api/a/admin/`), log in as administrator and add users.

**If something goes wrong**, the start window says what to do: Docker not installed, Docker not running, port in use. If it says DataGatherer did not start, send the messages shown above it to whoever maintains the app.

> Never delete the Docker *volumes* of DataGatherer (for example with `docker compose down -v`): they hold the database and the uploaded images.

### What the start script does
- Checks that Docker is installed and running.
- On the first start, creates `.env.docker` from `.env.docker.example` with new random passwords, and picks a free port (8080, or the next free one) saved as `APP_PORT`.
- Downloads the ready-made images published by CI on the GitHub Container Registry (`ghcr.io/videm02/datagatherer-backend` and `-nginx`, for Intel/AMD and ARM computers) and starts them. If the download is not possible, it builds them on the computer instead (10 to 20 minutes). Each start also downloads updates, if any.
- Waits until the app answers, then opens it in the browser.

## For Developers

- `start.sh` runs the published images, not your local code. To run your changes: `docker compose --env-file .env.docker up -d --build`.
- Images are published by `.github/workflows/images.yml` on every push to `main` (tag `latest`) and every git tag (tag = git tag name); every image also gets a `sha-<commit>` tag. Set `DATAGATHERER_VERSION` to run a specific one.
- Backend from the source folder (code changes without rebuilding):
  `docker compose --env-file .env.docker -f docker-compose.yml -f docker-compose.dev.yml up`
- Frontend: `cd frontend && npm ci && npm start` serves the app on `http://localhost:3000` and forwards `/a/`, `/b/` and `/media/` to the backend on `127.0.0.1:8000`.
- The superuser is created on the first start from `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` in `.env.docker`.
- Index computation is restricted to staff users. For backups, use `pg_dump` on the database container.

## Testing

- Backend: Unit tests cover critical data operations & matrix accuracy.
- Frontend: Currently not automatically tested (roadmap item).

Run backend tests in the backend container (they no longer run at every start):
```bash
docker compose --env-file .env.docker run --rm django python manage.py test
```

Outside Docker, set `DEBUG=1` (development only) or provide a `SECRET_KEY`: the backend refuses to start without a secret key when debug mode is off.

Frontend development: `cd frontend && npm start` serves the app on `http://localhost:3000` and forwards `/a/`, `/b/` and `/media/` to the backend on `127.0.0.1:8000`.

## Project Structure (Selected)

```
backend/
	data_gatherer/          # Django project root
	functions_api/          # Functions & shared logic
	job_api/                # Job orchestration
	storage_api/            # Persistence & serializers
	services/               # OCR, suggestion, indexing
frontend/                 # React SPA
nginx/                    # Reverse proxy config
docs/                     # Diagrams & documentation
```

## Extensibility

Add new extraction or analytics services by placing Python modules in `services/` and wiring tasks via `job_api` logic. Frontend queries can be added under `src/queries/` and consumed in state slices (e.g. `keyboardSlice.js`).

## Roadmap / Ideas

- Frontend automated testing (Jest + React Testing Library)
- Auth hardening (JWT / session rotation)
- Role‑based access & audit logging
- Pluggable storage backends (PostgreSQL, S3 for media)
- Advanced similarity & clustering visualizations
- Export matrix in multiple formats (CSV / Parquet)

## Contributing

Currently oriented toward personal / portfolio use. If you wish to contribute:
1. Fork & create a feature branch
2. Keep changes focused & documented
3. Open a PR describing intent & test impact

## License

License not specified. If publishing publicly, choose one (MIT / Apache‑2.0 / Proprietary) and update this section.

## Disclaimer

This repo demonstrates architectural and data processing approaches and is **not** production‑hardened. Use at your own risk.

---

Feel free to reach out or open issues for discussion, improvements, or clarifications.