import {Children} from "react";

const Card = ({title, children, rightAlignObjArray}) => {
    return (
        <div>
            <div className="card w-100 border-black">
                <div className="card-body">
                    <h3 className="card-title">{title}</h3>

                    {children ? <div className="card-body">{children}</div> : <></>}

                    {
                        rightAlignObjArray ?
                            <div className={"w-100 d-flex justify-content-end"}>
                                {Children.map(rightAlignObjArray, (child, i) =>
                                    <div key={i}>
                                        {child}
                                    </div>
                                )}
                            </div>
                            : <></>
                    }


                </div>
            </div>
        </div>
    )
}

export default Card

