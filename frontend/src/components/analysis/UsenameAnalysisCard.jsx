import Card from "../generic/Card";
import {useMutation, useQuery} from "@tanstack/react-query";
import {useEffect, useState} from "react";
import fetchIGUser from "../../queries/fetchUserHashtagUses";

import {patchAlias} from "../../queries/patchAlias";

const UsernameAnalysisCard = ({imgId}) => {
    const [content, setContent] = useState('Caricamento...')
    const [isCreatedByThisImage, setIsCreatedByThisImage] = useState(false)
    const [alias, setAlias] = useState('')
    const [userId, setUserId] = useState(null)

    const {data: rawFetchData, isError, isSuccess, error} = useQuery({
        queryKey: [`fetchImageCropData_${imgId}`],
        queryFn: () => fetchIGUser(imgId),
        retry: 1,
    })


    
    useEffect(() => {
        if (!rawFetchData) return
        if (rawFetchData.length === 0) {
            return
        }
        const fetchData = rawFetchData[0].igUser

        setContent(fetchData.name)
        setAlias(fetchData.alias)
        setUserId(fetchData.id)
        setIsCreatedByThisImage(
            fetchData.createdFromImage == imgId
        )

    }, [isSuccess]);


    if (isError) {
        return(
            <div>
                Err {error.error}
            </div>
        )
    }


    if (rawFetchData?.length === 0){
        return (
            <div className={'p-1 m-3 border border-black'}>
                Non essendo stato rilevato alcun hashtag, non è stata creata alcuna nuova
                associazione tra utente ed hashtag
            </div>
        )
    }


    return (
        <div className={"my-1"}>
            <Card title={"Instagram User"}>
                <div className={"mx-1"}>
                    <input
                        disabled={true}
                        className={"w-100 font-monospace"}
                        placeholder={"Testo riconosciuto..."}
                        value={`'${content}'`}
                        onChange={e => setContent(e.target.value)}
                    />
                </div>


                {
                    isCreatedByThisImage ?
                        <div className={"p-2 m-2 alert alert-warning"}>
                            Questo utente è stato creato da questa immagine.
                        </div>
                        : <></>
                }
            </Card>
        </div>
    )
}

export default UsernameAnalysisCard