import {useRef, useState} from "react";
import {canvasPreview} from "./canvasPreview";
import Card from "../../generic/Card";
import {useMutation, useQuery} from "@tanstack/react-query";
import {createImageCrop} from "../../../queries/createImageCrop";

import {doDefaultCrop} from "../../../queries/doDefaultCrop";
import HotButton from "../../hotstuff/HotButton";
import fetchImageCropAndLoadCrop from "../../../queries/fetchImageCropAndLoadCrop";
import {createDefaultCrop} from "../../../queries/createDefaultCrop";


const CompletedCanvas = ({previewCanvasRef}) => {
    return (
        <div className={"w-100 h-100"}>
            <canvas
                ref={previewCanvasRef}
                style={{
                    objectFit: 'contain',
                    width: "100%",
                    height: "100%"
                }}
            />
        </div>
    )
}


const ImageAnalysisCard = ({
                               vhHeight,
                               title,
                               completedCrop,
                               setIsCropEnabled,
                               imgRef,
                               setCrop,
                               imgId,
                               percentCrop,
                               prjId
                           }) => {


    const [isSetDefaultEnabled, setIsSetDefaultEnabled] = useState(false)
    const previewCanvasRef = useRef(null);



    const {data: cropData, error, refetch: cropDataRefetch} = useQuery({
        queryKey: [`fetchImageCropData_${title}`],
        queryFn: () =>
            fetchImageCropAndLoadCrop(
                imgId,
                title,
                imgRef,
                previewCanvasRef
            ),
        retry: 1,
    })


    const {mutate: doDefaultCropToTargetImageMutation} = useMutation({
        queryKey: [`useDefaultCrops_${title}`],
        mutationFn: () => doDefaultCrop({
            prjId,
            fieldName: title,
            targetImg: imgId
        }),
        retry: 1,
        onSuccess: () => cropDataRefetch(),
        onError: (error) => {alert(`Errore: ${error}`)}
    })


    const {mutate: doImageCroppingMutation} = useMutation({
        queryKey: ['createImageCrop'],
        mutationFn: () => createImageCrop({
            fieldName: title,
            imgId,
            percentCrop
        }),
        retry: 1,
        onSuccess: (data) => {
            setIsSetDefaultEnabled(true)
            cropDataRefetch()
        },
        onError: (error) => {
            alert("Errore nella creazione del ritaglio!" + error.message)
            console.log(error)
        }
    })


    const {mutate: createDefaultCropMutation} = useMutation({
        queryKey: ['setDefault'],
        mutationFn: () => createDefaultCrop({
            fieldName: title,
            prjId,
            percentCrop
        }),
        retry: 1,
        onSuccess: () => alert('Ritaglio impostato come default!'),
        onError: (error) => alert(`Errore nell'impostazione del ritaglio. Err: ${error}`)
    })




    const handleSaveCrop = () => {
        if (!imgRef.current || !completedCrop === null) return

        canvasPreview(
            imgRef.current,
            previewCanvasRef.current,
            completedCrop,
        )

        setIsCropEnabled(false)
        setCrop(null)

        doImageCroppingMutation()
    }




    if (error) {
        alert(`Errore nel caricamento del campo ${title}: ${error.message}`)
        return (
            <div>
                Errore!
            </div>
        )
    }



    return (
        <div className={"my-3"}>
            <Card title={title}>
                <div style={{height: vhHeight || "15vh"}}
                     className={"w-100 d-flex justify-content-center p-3 border border-black"}>
                    <CompletedCanvas previewCanvasRef={previewCanvasRef}/>

                </div>

                <div className={"w-100 h-100 d-flex"}>


                    <div>
                        <HotButton
                            uniqueHotKeyId={`set_default_${title}`}
                            className={"btn btn-primary my-2 mx-2"}
                            onClick={doDefaultCropToTargetImageMutation}
                        >
                            Usa il ritaglio di default
                        </HotButton>
                    </div>


                    <div>
                        <HotButton
                            className={"btn btn-primary my-2 mx-2"}
                            onClick={() => setIsCropEnabled(true)}
                            uniqueHotKeyId={`begin_crop_${title}`}
                        >
                            Inizia il ritaglio immagine
                        </HotButton>
                    </div>

                    <div>
                        <HotButton
                            uniqueHotKeyId={`finish_crop_${title}`}
                            className={"btn btn-primary my-2 mx-2"}
                            onClick={handleSaveCrop}
                        >
                            Concludi ritaglio immagine
                        </HotButton>
                    </div>


                    <div>
                        <button
                            disabled={!isSetDefaultEnabled}
                            className={"btn btn-primary my-2 mx-2"}
                            onClick={createDefaultCropMutation}
                        >
                            Salva il taglio come default
                        </button>
                    </div>

                </div>


                <div className={"mx-1"}>
                    <textarea
                        id={title}
                        className={"w-100 font-monospace"}
                        placeholder={"Testo riconosciuto"}
                        rows={5}
                        value={cropData?.recognizedText}
                        disabled={true}
                    />
                </div>

            </Card>
        </div>
    )
}

export default ImageAnalysisCard