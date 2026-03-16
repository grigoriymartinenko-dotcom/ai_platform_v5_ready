import {useState} from "react"

export default function Sidebar() {

    const [chats, setChats] = useState<string[]>([
        "Новый чат"
    ])

    const createChat = () => {

        setChats(prev => [
            "Новый чат",
            ...prev
        ])

    }

    return (

        <div className="w-64 bg-gray-900 text-white flex flex-col">

            <button
                onClick={createChat}
                className="m-3 p-2 bg-gray-700 rounded hover:bg-gray-600"
            >
                + Новый чат
            </button>

            <div className="flex-1 overflow-y-auto">

                {chats.map((chat, i) => (

                    <div
                        key={i}
                        className="p-3 hover:bg-gray-800 cursor-pointer"
                    >
                        {chat}
                    </div>

                ))}

            </div>

        </div>
    )
}