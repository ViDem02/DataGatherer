import axios from "axios";
import {defaultBaseUrl} from "../global_vars";
import getAuthAxiosConfig from "./common/getAuthAxiosConfig";

export const patchAlias = async ({id, alias}) => {
    const base = process.env.REACT_APP_API_URL || defaultBaseUrl
    const response = await axios.patch(
        base + `/b/storage_api/ig_users/${id}/`,
        {
            id: id,
            alias: alias
        },
        await getAuthAxiosConfig());
    return response.data;
};

