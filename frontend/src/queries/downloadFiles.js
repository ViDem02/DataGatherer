import axios from "axios";
import {defaultBaseUrl} from "../global_vars";
import getAuthAxiosConfig from "./common/getAuthAxiosConfig";

// Plain links can't carry the Bearer token, so files are fetched with it and then saved
const downloadAuthenticatedFile = async (path, filename) => {
    const base = process.env.REACT_APP_API_URL || defaultBaseUrl

    const response = await axios.get(
        base + path,
        {...await getAuthAxiosConfig(), responseType: 'blob'}
    )

    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
}

export const downloadMatrix = (prjId) => downloadAuthenticatedFile(`/b/fx_api/matrix/${prjId}/`, 'matrix.csv')
    .catch((error) => alert(`Errore nel download della matrice: ${error.message}`))
