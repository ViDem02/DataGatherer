import SingleImgAnalysisLayout from "../../layouts/single_image_analysis_layout/SingleImgAnalysisLayout";
import DataAnalysisCard from "../../components/analysis/DataAnalysisCard";
import {useParams, useSearchParams} from "react-router-dom";
import {defaultBaseUrl} from "../../global_vars";
import {useMutation, useQuery} from "@tanstack/react-query";
import fetchImage from "../../queries/fetchImage";
import {useRef, useState} from "react";
import {extendNetworkFromImage} from "../../queries/extendNetworkFromImage";
import HotButton from "../../components/hotstuff/HotButton";
import {structure_route} from "../data_structuring_page/DataStructuringPage";
import {gather_route} from "../data_gatering_page/DataGatheringPage";
import calculateIndex from "../../queries/calculateIndex";

export const edit_route =  (prjId, imgId) => `/prj/${prjId}/works/${imgId}/edit`

const DataEditingPage = () => {

    const {imgId,prjId} = useParams()

    const usernameSaveRef = useRef(null);
    const hashtagSaveRef = useRef(null);

    const [usernameSuccess, setUsernameSuccess] = useState(false)
    const [hashtagSuccess, setHashtagSuccess] = useState(false)

    const canMoveForwards = () => (
         usernameSuccess && hashtagSuccess
    )

    const {refetch: calcIndex} = useQuery({
        queryFn: () => calculateIndex(),
        retry: 1,
        enabled: false,
        queryKey: "calc_index"
    })

    const { data: imgData, error, isFetching} = useQuery({
        queryKey: ['get_scenario', imgId],
        queryFn: () => (fetchImage(imgId))
    });

    const {mutate: structureDataMutation} = useMutation({
        mutationFn: () => extendNetworkFromImage({
            targetImage: imgId
        }),
        retry: 1,
        onSuccess: () => {
            window.location.href = structure_route(prjId, imgId)
        },
        onError: (error) => {
            console.log(error)
            alert("Errore nella creazione dei dati strutturati: " + JSON.stringify(error.body))
        }
    })

    const handleForward = () => {
        structureDataMutation({targetImage: imgId})
    }



    const handleSaveData = () => {
        usernameSaveRef.current.click()
        hashtagSaveRef.current.click()
    }



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


    const baseUrl = process.env.REACT_APP_API_URL || defaultBaseUrl
    const imgUrl = baseUrl + imgData.image_file_url

    return (
        <SingleImgAnalysisLayout

            leftChildren={
                <div className={"w-100 h-100"}>
                    <img
                        className={"w-100 h-100 object-fit-contain"}
                        src={imgUrl}
                        alt={"Immagine in analisi"}
                    />
                </div>
            }

            rightChildren={
                <div>

                    <DataAnalysisCard
                        title={"Username"}
                        alreadyExists={false}
                        imgId={imgId}
                        btnRef={usernameSaveRef}
                        rows={4}
                        setParentSuccess={setUsernameSuccess}
                        suggestionsAllowed={true}
                    />

                    <DataAnalysisCard
                        title={"Hashtags"}
                        rows={6}
                        imgId={imgId}
                        btnRef={hashtagSaveRef}
                        infoText={"Tutti gli hashtags verranno creati a lettere minuscole e la " +
                            "punteggiatura, all'interno o alla fine degli hashtags " +
                            "(!\"#$%&'()*+, -./:;<=>?@[\\]^_`{|}~) non verrà considerata. Gli hashtags " +
                            "possono essere scritti senza spazi tra uno e l'altro (i.e. #ciao#sus)"}
                        setParentSuccess={setHashtagSuccess}
                    />

                </div>
            }


            bottomChildren={
                <div className={"d-flex justify-content-center h-100 align-items-center bg-dark-subtle w-100"}>
                    <HotButton
                        style={{width: "20vw"}}
                        className={`btn my-2 mx-2 btn-primary`}
                        onClick={() => window.location.href = gather_route(prjId, imgId)}
                        uniqueHotKeyId={'back_data_edit'}
                    >
                        Indietro
                    </HotButton>

                    <HotButton
                        style={{width: "20vw"}}
                        className={`btn my-2 mx-2 btn-primary`}
                        onClick={handleSaveData}
                        uniqueHotKeyId={'save_data_data_edit'}
                    >
                        Salva tutti i dati
                    </HotButton>

                    <HotButton
                        style={{width: "20vw"}}
                        className={`btn my-2 mx-2 btn-primary`}
                        onClick={() => calcIndex()}
                        uniqueHotKeyId={'recalc_calc_index'}
                    >
                        Ricalcola indice
                    </HotButton>

                    <HotButton
                        disabled={!canMoveForwards()}
                        style={{width: "20vw"}}
                        className={"btn btn-primary my-2 mx-2"}
                        uniqueHotKeyId={'next_data_edit'}
                        onClick={handleForward}
                    >
                        Estendi network e procedi
                    </HotButton>
                </div>
            }
        />
    )
}

export default DataEditingPage