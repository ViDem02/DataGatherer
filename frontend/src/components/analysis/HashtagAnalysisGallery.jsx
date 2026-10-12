import Card from "../generic/Card";
import {useQuery} from "@tanstack/react-query";
import {useEffect, useState} from "react";
import fetchIGUser from "../../queries/fetchUserHashtagUses";

import fetchUserHashtagUses from "../../queries/fetchUserHashtagUses";


const HashtagAnalysisCard = ({propContent, propIsCreatedByThisImage, propObjId}) => {

    const [objId, setObjId] = useState(propObjId)
    const [content, setContent] = useState(propContent)
    const [isCreatedByThisImage, setIsCreatedByThisImage] = useState(propIsCreatedByThisImage)

    return (
        <div className={"my-1"}>
            <Card title={"Hashtag"}>
                <div className={'d-flex w-100 align-items-center'}>
                    <div className={'h3 mx-1'}>
                        #
                    </div>
                    <div className={'w-100'}>
                        <div className={""}>
                            <input
                                className={"w-100 font-monospace"}
                                placeholder={"Testo riconosciuto..."}
                                value={content}
                                disabled={true}
                                onChange={e => setContent(e.target.value)}
                            />
                        </div>
                        {
                            isCreatedByThisImage ?
                                <div className={"p-2 my-2 alert alert-warning"}>
                                    Questo hashtag è stato creato da questa immagine.
                                </div>
                                : <></>
                        }
                    </div>
                </div>
            </Card>
        </div>
    )
}


const HashtagAnalysisGallery = ({imgId}) => {
    const {data: hashtagData, isError, isFetching} = useQuery({
        queryKey: [`fetchImageCropData_${imgId}`],
        queryFn: () => fetchUserHashtagUses(imgId),
        retry: 1,
    })


    if (isError) {
        return (
            <div>
                ERRORRE!!!!!
            </div>
        )
    }

    if (isFetching) {
        return (
            <div>
                Caricamento...
            </div>
        )
    }

    return (
        <div>
            {
                hashtagData.map((child, i) => {
                        const hash = child.hashtag
                        return (
                            <HashtagAnalysisCard
                                propContent={`'${hash.content}'`}
                                propIsCreatedByThisImage={
                                    hash.createdFromImage == imgId
                                }
                                propObjId={hash.id}
                            />
                        )
                    }
                )
            }
        </div>
    )
}

export default HashtagAnalysisGallery