import {useRef} from "react";
import {useCookies} from "react-cookie";
import Navbar from "../../components/auth/Navbar";

const SingleImgAnalysisLayout = ({leftChildren, rightChildren, bottomChildren, imageUserId}) => {

    const leftRef = useRef(null);

    const [cookies, setCookie] = useCookies(['left_panel_width']);

    setInterval(
        () => {
            if (!leftRef) return
            let value = leftRef.current?.getBoundingClientRect().width
            if (value === undefined) return
            setCookie('width', value)
        },
        2000
    )

    const finalLeftWidth = cookies.width ? `${cookies.width}px` : '30vw'

    return (
        <div>
            <Navbar/>
            {
                imageUserId ?
                    <h1>
                        Raccolta Dati, IMG <span className={"font-monospace"}>{imageUserId}</span>
                    </h1>
                    :
                    <h1>
                        Raccolta Dati
                    </h1>
            }
            <div className={"w-100 d-flex"}>
                <div
                    style={{
                        marginRight: "10px",
                        height: "78vh",
                    }}
                    className={"px-5"}
                >
                    <div
                        style={{
                            overflow: "auto",
                            width: finalLeftWidth,
                            resize: "horizontal",
                            height: "100%",
                            borderRight: "solid gray 2px",
                        }}
                        ref={leftRef}
                    >
                        <div className={"h-100"}>
                            {leftChildren}
                        </div>
                    </div>
                </div>


                <div style={{width: "100%", height: "78vh"}} className={"p-5"}>
                    <div className={"h-100 overflow-y-scroll"}>
                        <div>
                            {rightChildren}
                        </div>
                    </div>
                </div>
            </div>

            <div style={{height: "10vh"}} className={"d-flex w-100 justify-content-center py-2"}>
                {bottomChildren}
            </div>

        </div>
    )
}



export default SingleImgAnalysisLayout