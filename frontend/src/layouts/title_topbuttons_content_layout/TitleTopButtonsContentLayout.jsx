import Navbar from "../../components/auth/Navbar";

const TitleTopButtonsContentLayout = ({title, topButtons, content}) => {
    return (
        <div>
            <Navbar/>
            <div className={"h1 m-5"}>
                {title}
            </div>

            <div className={'d-flex flex-wrap m-5'}>
                {topButtons.map((child, i) => (
                    <div key={i}>
                        {child}
                    </div>
                ))}
            </div>

            <div className={'m-5'}>
                {content}
            </div>

        </div>
    )
}


export default TitleTopButtonsContentLayout