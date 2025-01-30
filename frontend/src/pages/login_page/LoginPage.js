import {useState} from "react";
import {useMutation} from "@tanstack/react-query";
import {extendNetworkFromImage} from "../../queries/extendNetworkFromImage";
import {structure_route} from "../data_structuring_page/DataStructuringPage";
import {doLogin} from "../../queries/doLogin";
import Cookies from 'universal-cookie';

const LoginPage = () => {



    const {mutate: loginMutation} = useMutation({
        mutationFn: () => doLogin({
            username: username, password: password
        }),
        retry: 1,
        onSuccess: (response) => {
            const cookies = new Cookies(null, { path: '/' })
            cookies.set('access', response.access)
            cookies.set('refresh', response.refresh)
            cookies.set('username', username)

            const current = cookies.get('current')
            if (current !== undefined){
                window.location.assign(current)
                return
            }
            window.location.assign('/')
        },
        onError: (error) => {
            console.log(error)
            setIsLoading(false)
            alert("Errore nel login")
        },
        onMutate: () => {setIsLoading(true)}
    })

    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    return (
        <div className={'d-flex justify-content-center align-items-center flex-column'} style={{height: "100vh"}}>
            <div className={"card p-5 rounded-2 d-flex flex-column justify-content-center"}>
                <div className={'h1 m-3'}>Data Gatherer</div>
                <div  className="input-group input-group-sm mb-3">
                    <span className="input-group-text w-25" id="inputGroup-sizing-sm">User</span>
                    <input autoFocus={true} tabIndex={1} type="text" className="form-control" aria-label="Sizing example input"
                           value={username} onChange={(e) => setUsername(e.target.value)}
                           aria-describedby="inputGroup-sizing-sm"/>
                </div>
                <div  className="input-group input-group-sm mb-3">
                    <span className="input-group-text w-25" id="inputGroup-sizing-sm">Pass</span>
                    <input tabIndex={2} type="password" className="form-control" aria-label="Sizing example input"
                           value={password} onChange={(e) => setPassword(e.target.value)}
                           aria-describedby="inputGroup-sizing-sm"/>
                </div>
                <button tabIndex={3} className={"btn btn-success m-3"} onClick={() => loginMutation()}>
                    {isLoading ? "Loading...." : "Submit"}
                </button>
            </div>
        </div>
    )

}

export default LoginPage