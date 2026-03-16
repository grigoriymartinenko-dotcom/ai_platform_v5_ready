import {useState} from "react"

export default function ChatInput({onSend}: { onSend: (msg: string) => void }) {

    const [text, setText] = useState("")

    function send() {

        if (!text.trim()) return

        onSend(text)

        setText("")

    }

    return (

        <div className="border-t p-4 flex">

            <input
                className="flex-1 border rounded p-2"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Напиши сообщение..."
            />

            <button
                onClick={send}
                className="ml-2 px-4 bg-blue-500 text-white rounded"
            >
                Send
            </button>

        </div>

    )

}