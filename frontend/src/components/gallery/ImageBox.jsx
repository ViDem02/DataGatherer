import {defaultBaseUrl} from "../../global_vars";
import {useMutation} from "@tanstack/react-query";
import {deleteImage} from "../../queries/deleteImage";
import {useRef} from "react";
import {gather_route} from "../../pages/data_gatering_page/DataGatheringPage";

const ImageBox = ({showImage, prjDataRefetch, userId, isDataGathered, imageFileUrl, imgId, is_similar_to_user_id, prjId}) => {

    const mainRef = useRef(null);

    let specificStyle = {
        height: "140px",
        width: "90px",
        backgroundColor: "gray"
    }


    const {mutate: deleteMutate} = useMutation({
        mutationFn: deleteImage,
        retry: 1,
        onSuccess: () => {
            mainRef.current.style.display = "none"
            prjDataRefetch()
        },
        onError: (error) => {
            alert("Errore di connessione: " + error.message)
            console.log(error)
        }
    })

    let base = process.env.REACT_APP_API_URL || defaultBaseUrl
    let source = base + imageFileUrl

    const handleDeleteImage = () => {
        if (isDataGathered){
            if (!window.confirm("Si vuole davvero eliminare l'immagine? Verranno eliminate anche tutte le " +
                "connessioni utente - hashtags.")) return
        }
        deleteMutate(imgId)
    }

    return (
        <div ref={mainRef} className={`rounded-3 m-3 ${isDataGathered ? "bg-success-subtle" : "bg-danger-subtle"}` }>

            <div className={"m-2"} >

                <div className={"d-flex justify-content-center w-100"}>
                    <div style={specificStyle}>
                        {
                            showImage ?
                                <img src={source} className={"h-100 w-100"} alt={"immagine da lavoro"}/>
                                : <></>
                        }
                    </div>
                </div>


                <div className={"w-100 h4 text-center font-monospace"}>
                    {userId}
                </div>


                <div className={"d-flex w-100 justify-content-center"}>
                    <button
                        disabled={isDataGathered}
                        onClick={() => window.location.href = gather_route(prjId, imgId)}
                        className="btn btn-primary m-2" >ANYZ
                    </button>

                    <button href="#"  disabled={isDataGathered} className="btn btn-danger m-2" onClick={handleDeleteImage}>DEL</button>
                </div>

                {
                    is_similar_to_user_id ?
                        <div className={"w-100 text-center alert p-1 alert-warning"}>
                            Simile a {is_similar_to_user_id}
                        </div>
                        :<></>
                }
            </div>
        </div>
    )
}

export default ImageBox