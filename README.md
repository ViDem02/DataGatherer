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
1. Port `8080` is not exposed publicly (restrict firewall / router). 
2. Every secret in `.env.docker` is unique and random (it is git‑ignored; never commit it).
3. Uploaded media does not contain sensitive PII unless you harden access: media files are served without authentication to anyone who knows their URL.

> Important: No built‑in authentication hardening or role‑based access beyond Django’s defaults. You are responsible for securing deployments.

## Prerequisites

Ensure you have:
- Docker & Docker Compose (v2+)
- (Optional) Python 3.11+ if running backend outside containers

## Quick Start

```bash
git clone https://github.com/ViDem02/DataGatherer.git
cd DataGatherer
cp .env.docker.example .env.docker   # then replace every "change-me" value
docker compose build
docker compose up
```

Then open: `http://127.0.0.1:8080`

## Accessing the Admin

URL: `http://127.0.0.1:8080/api/a/admin/`

The superuser is provisioned on first run from `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` in `.env.docker`.
Index computation is restricted to staff users. For backups, use `python manage.py dumpdata` (or `pg_dump`) on the server.

## Testing

- Backend: Unit tests cover critical data operations & matrix accuracy.
- Frontend: Currently not automatically tested (roadmap item).

Run backend tests (inside the backend container or a Python venv):
```bash
python manage.py test
```

Outside Docker, set `DEBUG=1` (development only) or provide a `SECRET_KEY`: the backend refuses to start without a secret key when debug mode is off.

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