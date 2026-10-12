// Same origin by default: nginx (production) or the Vite dev proxy (development) forwards API calls to Django.
// The login cookies are only sent to the same site, so the API must not live on another host.
export const defaultBaseUrl = ""