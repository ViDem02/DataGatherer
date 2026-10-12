import Card from "../../components/generic/Card";
import {useMutation, useQuery} from "@tanstack/react-query";
import fetchProjects from "../../queries/fetchProjects";
import {deleteProject} from "../../queries/deleteProject";
import {createProject} from "../../queries/createProject";
import {defaultBaseUrl} from "../../global_vars";
import TitleTopButtonsContentLayout from "../../layouts/title_topbuttons_content_layout/TitleTopButtonsContentLayout";
import {adminUrl} from "../../api_router/fx_api";
import {overview_route} from "../project_overview_page/ProjectOverviewPage";


const HomePage = () => {

    const {data: projects, error} = useQuery({
        queryKey: ['get_scenario'],
        queryFn: fetchProjects,
    });

    const {mutate: deletePrjMutate} = useMutation({
        mutationFn: deleteProject,
        retry: 1,
        onSuccess: () => window.location.reload(),
        onError: (error) => alert("Errore nell'eliminazione: " + error.message)
    })

    const {mutate: createPrjMutate} = useMutation({
        mutationFn: createProject,
        retry: 1,
        onSuccess: () => window.location.reload(),
        onError: (error) => alert("Errore nella creazione!" + error.message)
    })

    const handleCreate = () => {
        createPrjMutate(prompt("Nome del progetto?"))
    }

    const handleDelete = (id) => {
        if (!window.confirm('Si è sicuri di voler cancellare il progetto?')) return
        deletePrjMutate(id)
    };


    const ProjectCard = ({child}) => (
        <div className={"my-5 w-75"}>
            <Card title={child.name} rightAlignObjArray={[

                <a
                    href={overview_route(child.id)}
                    className="btn btn-primary m-2"
                >
                    Entra
                </a>,

                <button
                    onClick={() => handleDelete(child.id)}
                    className="btn btn-danger m-2">
                    Elimina
                </button>

            ]}/>
        </div>
    )


    if (error) return (
        <div>
            Errore! {error.message}
        </div>
    )

    if (!projects) return (
        <></>
    )

    return (
        <TitleTopButtonsContentLayout
            title={'Progetti'}
            topButtons={[
                    <div className={"m-2"}>
                        <button className="btn btn-success" onClick={handleCreate}>Crea nuovo progetto</button>
                    </div>,

                    <div className={"m-2"}>
                        <a href={adminUrl()} className="btn btn-primary mx-1">
                            Apri pannello di controllo entità
                        </a>
                    </div>
                ]}
            content={
                projects.map((child, i) => (
                    <ProjectCard child={child} key={i}/>
                ))
            }
        />
    )
}

export default HomePage