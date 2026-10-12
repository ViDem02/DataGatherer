import {defaultBaseUrl} from "../global_vars";

export const serverUrl = process.env.REACT_APP_API_URL || defaultBaseUrl

export const adminUrl = () => serverUrl + '/a/admin/'