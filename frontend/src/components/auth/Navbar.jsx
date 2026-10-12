import Cookies from "universal-cookie";


const Navbar = () => {
    const cookies = new Cookies(null, { path: '/' });

    const handleLogout = () => {
        cookies.remove('access')
        cookies.remove('refresh')
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