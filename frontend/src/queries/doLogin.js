import {defaultBaseUrl} from "../global_vars";
import axios from "axios";

export const doLogin = async ({username, password}) => {
    const base = process.env.REACT_APP_API_URL || defaultBaseUrl
    // The tokens come back as HttpOnly cookies set by the server
    const response = await axios.post(
        base + '/a/token/obtain/',
        {username, password},
        {withCredentials: true});
    return response.data;
}
