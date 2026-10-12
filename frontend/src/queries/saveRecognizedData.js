import axios from "axios";
import {defaultBaseUrl} from "../global_vars";
import getAuthAxiosConfig from "./common/getAuthAxiosConfig";

export const saveRecognizedData = async ({id, recognizedData}) => {
    const base = process.env.REACT_APP_API_URL || defaultBaseUrl
    await axios.patch(
        base + `/b/storage_api/img_crops/${id}/`,
        {
            id: id,
            recognizedText: recognizedData
        },
        await getAuthAxiosConfig());

    return {};
};

