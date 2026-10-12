import Cookies from "universal-cookie";
import axios from "axios";
import {defaultBaseUrl} from "../../global_vars";


const Navbar = () => {
    const cookies = new Cookies(null, { path: '/' });

    const handleLogout = async () => {
        const base = process.env.REACT_APP_API_URL || defaultBaseUrl
        // The login cookies are HttpOnly: only the server can revoke and delete them
        await axios.post(base + '/a/token/logout/', {}, {withCredentials: true}).catch(console.log)
        cookies.remove('username')
        document.location = '/login'
    }

    return(
        <div className={"border-bottom border-primary w-100 mb-2-subtle p-2 d-flex justify-content-between align-content-center"}>
            <div className={"text-primary d-flex align-items-center"}>
                Logged in as: <span className={"font-monospace m-1"}>{cookies.get('username')}</span>
            </div>
            <div>
                <button className={"btn btn-outline-primary btn-sm"} onClick={handleLogout}> Logout </button>
            </div>
        </div>
    )
}

export default Navbar