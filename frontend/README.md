# DataGatherer frontend

React app built with [Vite](https://vite.dev/).

- `npm start`: development server on http://localhost:3000. API calls (`/a/`, `/b/`, `/media/`) are forwarded to the backend on `127.0.0.1:8000`, so the login cookies stay on one origin.
- `npm run build`: production build in `build/`, served by nginx (see `docker-compose.yml`). The API base URL comes from `.env.production` (`REACT_APP_API_URL`).
- `npm run preview`: serves the production build locally.

Files containing JSX use the `.jsx` extension.
