import Navbar from "../../components/auth/Navbar";
import {useParams} from "react-router-dom";
import {useMutation, useQuery} from "@tanstack/react-query";
import fetchProjects from "../../queries/fetchProjects";
import fetchProject from "../../queries/fetchProjectData";
import {useRef, useState} from "react";
import {uploadImages} from "../../queries/uploadImages";
import {overview_route} from "../project_overview_page/ProjectOverviewPage";

export const upload_route = (prj_id) => `/upload/${prj_id}/`

const UploadPage = () => {

    const fileInputRef = useRef();

    const {prjId} = useParams()
    const [filesValue, setFilesValue] = useState([])
    const [isLoading, setIsLoading] = useState(false)


    const {mutate: uploadMutate} = useMutation({
        mutationFn: () => uploadImages({
            files:fileInputRef.current.files, prjId
        }),
        retry: 1,
        onSuccess: (res) => {
            console.log("ok")
            window.location = overview_route(prjId)
        },
        onMutate: () => {setIsLoading(true)},
        onError: (error) => {
            alert(error.message)
            setIsLoading(false)
        },
    })

    const {
        data: projectData,
        isFetching,
        error: fetchingError,
    } = useQuery({
        queryFn: () => fetchProject(prjId),
        retry: 1
    })

    if (fetchingError){
        return <div>
            Errore: {fetchingError.message}
        </div>
    }

    return (<div>
        <Navbar/>
        <div className={'d-flex justify-content-center align-items-center flex-column'} style={{height: "93vh"}}>
            <div className={"card p-5 rounded-2 d-flex flex-column justify-content-center"}>
                <div className={'h1 m-3'}>Carica immagini</div>
                <div className="input-group input-group-sm mb-3">
                    <span className="input-group-text w-25" id="inputGroup-sizing-sm">Progetto</span>
                    <input tabIndex={-1} disabled={true} type="text" className="form-control"
                           aria-label="Sizing example input"
                           value={isFetching ? "loading..." : projectData.name}
                           aria-describedby="inputGroup-sizing-sm"/>
                </div>
                <div className="input-group input-group-sm mb-3">
                    <input tabIndex={2} autoFocus={true} type="file" name={"files"} id={"id_files"} className="form-control"
                           aria-label="Sizing example input"
                           aria-describedby="inputGroup-sizing-sm"
                           placeholder={"Files"}
                           multiple={true}
                           ref={fileInputRef}
                    />
                </div>
                <button tabIndex={3} className={"btn btn-success m-3"} onClick={uploadMutate} >
                    {isLoading ? "Caricamento...." : "Carica"}
                </button>
            </div>
        </div>
    </div>)
}

export default UploadPage