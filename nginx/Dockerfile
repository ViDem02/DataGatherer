# Built from the repository root (see docker-compose.yml)

# Builds the React app, so the computer running DataGatherer needs no Node.js.
# The result is plain files, so it is built once on the build machine's own platform, not emulated per platform.
FROM --platform=$BUILDPLATFORM node:22-slim AS frontend

WORKDIR /srv/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build


FROM nginx:stable-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx/include.websocket /etc/nginx/app/include.websocket
COPY nginx/include.forwarded /etc/nginx/app/include.forwarded
COPY nginx/nginx.conf /etc/nginx/conf.d
COPY --from=frontend /srv/frontend/build /srv/frontend
