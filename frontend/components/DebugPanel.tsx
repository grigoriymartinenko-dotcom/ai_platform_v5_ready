export default function DebugPanel({logs}: { logs: string[] }) {

    return (

        <div className="w-96 bg-black text-green-400 text-sm p-3 overflow-y-auto">

            <div className="font-bold mb-2">
                Agent Debug
            </div>

            {logs.map((l, i) => (
                <div key={i}>
                    {l}
                </div>
            ))}

        </div>

    )

}