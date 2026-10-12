import axios from "axios";
import {defaultBaseUrl} from "../../global_vars";
import Cookies from "universal-cookie";

function handleGoToLogin(cookies){
    const current = document.location.pathname
    cookies.set('current', current)
    document.location.assign('/login')
}

// The login tokens are HttpOnly cookies that this code can't read: the browser sends them by itself.
// When the access token has expired (401), get a new one once from the refresh cookie and retry.
let refreshing = null

axios.interceptors.response.use(undefined, async (error) => {
    const request = error.config
    const isTokenCall = request?.url?.includes('/a/token/')

    if (error.response?.status !== 401 || !request || isTokenCall) {
        throw error
    }

    const cookies = new Cookies(null, { path: '/' });
    if (request._retried) {
        handleGoToLogin(cookies)
        throw error
    }
    request._retried = true

    const base = process.env.REACT_APP_API_URL || defaultBaseUrl
    try {
        refreshing = refreshing || axios.post(base + `/a/token/refresh/`, {}, {withCredentials: true})
        await refreshing
    } catch {
        handleGoToLogin(cookies)
        throw error
    } finally {
        refreshing = null
    }

    request.headers['X-CSRFToken'] = cookies.get('csrftoken')
    return axios(request)
})

export default async function getAuthAxiosConfig() {
    const cookies = new Cookies(null, { path: '/' });

    cookies.remove('current')

    return {
        withCredentials: true,
        headers: {
            // Cookie-authenticated requests are only accepted with the CSRF token
            'X-CSRFToken': cookies.get('csrftoken')
        }
    }
}
