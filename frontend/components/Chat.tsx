import {useChat} from "../hooks/useChat"
import Message from "./Message"
import ChatInput from "./ChatInput"

export default function Chat() {

    const {messages, loading, send} = useChat()

    return (

        <div className="flex flex-col h-full">

            <div className="flex-1 overflow-y-auto p-6 space-y-4">

                {messages.map((m, i) => (
                    <Message
                        key={i}
                        role={m.role}
                        content={m.content}
                    />
                ))}

                {loading && (
                    <div className="text-gray-500">
                        thinking...
                    </div>
                )}

            </div>

            <ChatInput onSend={send}/>

        </div>

    )

}