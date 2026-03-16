import Sidebar from "./Sidebar"

export default function Layout({children}: { children: any }) {

    return (

        <div className="flex h-screen">

            <Sidebar/>

            <main className="flex-1">
                {children}
            </main>

        </div>

    )

}