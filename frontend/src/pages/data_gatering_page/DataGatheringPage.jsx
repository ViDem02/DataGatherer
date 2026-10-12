import {useRef, useState} from "react";
import ReactCrop from "react-image-crop";
import ImageAnalysisCard from "../../components/analysis/image_analysis_card/ImageAnalysisCard";
import SingleImgAnalysisLayout from "../../layouts/single_image_analysis_layout/SingleImgAnalysisLayout";
import {useQuery} from "@tanstack/react-query";
import fetchImage from "../../queries/fetchImage";
import {useMatch, useParams} from "react-router-dom";
import HotButton from "../../components/hotstuff/HotButton";
import {serverUrl} from "../../api_router/fx_api";

// extremely important
import 'react-image-crop/dist/ReactCrop.css'
import {edit_route} from "../data_editing_page/DataEditingPage";
import {overview_route} from "../project_overview_page/ProjectOverviewPage";


export const gather_route =  (prjId, imgId) => `/prj/${prjId}/works/${imgId}/gather`

const DataGatheringPage = () => {

    const {imgId,prjId} = useParams()

    const [crop, setCrop] = useState()
    const [completedCrop, setCompletedCrop] = useState()
    const [percentCrop, setPercentCrop] = useState(null)
    const [isCropEnabled, setIsCropEnabled] = useState(false);

    const imgRef = useRef(null)


    const {data: imgData, error, isFetching} = useQuery({
        queryKey: ['get_scenario', imgId],
        queryFn: () => (fetchImage(imgId))
    });



    if (error) {
        return (
            <div>
                Error! {error.message}
            </div>
        )
    }

    if (isFetching){
        return (
            <div>
                Caricamento...
            </div>
        )
    }

    const url = serverUrl + imgData.image_file_url

    return (
        <SingleImgAnalysisLayout

            imageUserId={imgData.userId}

            leftChildren={
                <div className={"w-100 h-100"}>
                    <ReactCrop
                        disabled={!isCropEnabled}
                        crop={crop}
                        onComplete={(crop, percentCrop) => {
                            setCompletedCrop(crop)
                            setPercentCrop(percentCrop)
                        }}
                        onChange={c => setCrop(c)}
                    >
                        <img
                            className={"w-100 h-100 object-fit-contain"}
                            src={url}
                            alt={"Immagine in analisi"}
                            ref={imgRef}
                        />
                    </ReactCrop>
                </div>
            }

            rightChildren={
                <div>


                    <ImageAnalysisCard
                        imgId={imgData.id}
                        title={"Hashtags"}
                        completedCrop={completedCrop}
                        vhHeight={"25vh"}
                        setIsCropEnabled={setIsCropEnabled}
                        imgRef={imgRef}
                        setCrop={setCrop}
                        percentCrop={percentCrop}
                        prjId={prjId}
                    />

                    <ImageAnalysisCard
                        imgId={imgData.id}
                        title={"Username"}
                        completedCrop={completedCrop}
                        setIsCropEnabled={setIsCropEnabled}
                        imgRef={imgRef}
                        setCrop={setCrop}
                        percentCrop={percentCrop}
                        prjId={prjId}
                    />




                </div>
            }

            bottomChildren={

                <div className={"d-flex justify-content-center h-100 align-items-center bg-dark-subtle w-100"}>
                    <HotButton
                        style={{width: "20vw"}}
                        className={`btn my-2 mx-2 btn-primary`}
                        onClick={() => window.location.href = overview_route(prjId)}
                        uniqueHotKeyId={'back_to_home'}
                    >
                        Torna alla home
                    </HotButton>


                    <HotButton
                        style={{width: "20vw"}}
                        className={"btn btn-primary my-2 mx-2"}
                        onClick={() => {window.location.href = edit_route(prjId, imgId)}}
                        uniqueHotKeyId={'data_gathering_next'}
                    >
                        Avanti
                    </HotButton>
                </div>
            }
        />
    )
}

export default DataGatheringPage