import ReactMarkdown from "react-markdown"

type Props = {
    role: "user" | "assistant"
    content: string
}

export default function Message({role, content}: Props) {

    const isUser = role === "user"

    return (

        <div className={`w-full flex ${isUser ? "justify-end" : "justify-start"}`}>

            <div className={`max-w-2xl p-3 rounded-lg ${
                isUser
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
            }`}>

                <ReactMarkdown>
                    {content}
                </ReactMarkdown>

            </div>

        </div>

    )
}