import Gallery from "../../components/gallery/Gallery";
import {useParams, useSearchParams} from "react-router-dom";
import {useQuery} from "@tanstack/react-query";
import fetchProject from "../../queries/fetchProjectData";
import {downloadMatrix} from "../../queries/downloadFiles";
import TitleTopButtonsContentLayout from "../../layouts/title_topbuttons_content_layout/TitleTopButtonsContentLayout";
import {gather_route} from "../data_gatering_page/DataGatheringPage";
import {useState} from "react";
import {upload_route} from "../upload_page/UploadPage";
import calculateIndex from "../../queries/calculateIndex";


export const overview_route =  (prjId) => `/prj/${prjId}/`


const GatherButtons = ({next_image_to_analyze, are_all_images_analyzed, prjId}) => (
    !are_all_images_analyzed ?
        <a href={gather_route(prjId, next_image_to_analyze)} className="btn btn-primary mx-1">
            Raccogli dati dalle immagini non valutate
        </a>
        :
        <></>
)




const ProjectOverviewPage = () => {

    const { prjId } = useParams();

    const [showImages, setShowImages] = useState(false)

    const {
        data: projectData,
        isFetching,
        error: fetchingError,
        refetch: projectDataRefetch
    } = useQuery({
        queryFn: () => fetchProject(prjId),
        retry: 1,
        queryKey: "fetchProjectData"
    })

    const {refetch: calcIndex} = useQuery({
        queryFn: () => calculateIndex(),
        retry: 1,
        enabled: false,
        queryKey: "calc_index"
    })



    if (isFetching) {
        return <div>
            Caricamento dati progetto...
        </div>
    }

    if (fetchingError){
        return <div>
            Errore: {fetchingError.message}
        </div>
    }

    return (
        <TitleTopButtonsContentLayout
            title={`Progetto ${projectData.name}`}

            topButtons={[
                <div className={"m-2"}>
                    <a href={'/'} className="btn btn-primary mx-1">Torna ai progetti</a>
                </div>,

                <div className={"m-2"}>
                    <a href={upload_route(prjId)} className="btn btn-primary mx-1">Carica immagini in un progetto</a>
                </div>,


                <div className={"m-2"}>
                    <a onClick={() => downloadMatrix(prjId)} className="btn btn-primary mx-1">Scarica matrice formata</a>
                </div>,

                <div className={"m-2"}>
                    <a onClick={() => setShowImages(!showImages)} className="btn btn-primary mx-1">Mostra o nascondi immagini</a>
                </div>,

                <div className={"m-2"}>
                    <a onClick={() => calcIndex()} className="btn btn-primary mx-1">Calc index</a>
                </div>,

                <div className={'m-2'}>
                    <GatherButtons
                        prjId={prjId}
                        next_image_to_analyze={projectData.next_image_to_analyze}
                        are_all_images_analyzed={projectData.are_all_images_analyzed}
                    />
                </div>
            ]}

            content={
                <div>
                    <div>
                        users: {projectData.nr_users}, hashtags: {projectData.nr_hashtags}
                    </div>
                    <Gallery prjDataRefetch={projectDataRefetch} prjId={prjId} showImages={showImages}/>

                </div>
            }
        />
    )
}


export default ProjectOverviewPage