import {useState} from "react"

export function useChat() {

    const [messages, setMessages] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    async function send(message: string) {

        if (!message.trim()) return

        setMessages(prev => [
            ...prev,
            {role: "user", content: message}
        ])

        setLoading(true)

        const res = await fetch("/api/chat_stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message})
        })

        if (!res.body) return

        const reader = res.body.getReader()
        const decoder = new TextDecoder()

        let assistant = ""

        setMessages(prev => [
            ...prev,
            {role: "assistant", content: ""}
        ])

        while (true) {

            const {done, value} = await reader.read()

            if (done) break

            const chunk = decoder.decode(value)

            assistant += chunk

            setMessages(prev => {

                const updated = [...prev]

                updated[updated.length - 1].content = assistant

                return updated

            })

        }

        setLoading(false)

    }

    return {
        messages,
        loading,
        send
    }

}