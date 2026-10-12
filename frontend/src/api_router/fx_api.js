import {defaultBaseUrl} from "../global_vars";

export const serverUrl = process.env.REACT_APP_API_URL || defaultBaseUrl

export const adminUrl = () => serverUrl + '/a/admin/'

// Media paths come from the backend as absolute paths (e.g. "/api/media/imgs/..."): resolve them on the server's origin
export const mediaUrl = (path) => new URL(path, new URL(serverUrl, window.location.origin)).href