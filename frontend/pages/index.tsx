import {useState, useRef, useEffect} from "react";

export default function Home() {
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    // Автоскролл вниз при новых сообщениях
    useEffect(() => {
        bottomRef.current?.scrollIntoView({behavior: "smooth"});
    }, [messages, loading]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const msg = input.trim();
        setMessages((prev) => [...prev, {role: "user", content: msg}]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("/api/chat_stream", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: msg}),
            });

            if (!res.body) throw new Error("No stream");

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = "";

            // Добавляем пустое сообщение ассистента, чтобы потом обновлять
            setMessages((prev) => [...prev, {role: "assistant", content: ""}]);

            while (true) {
                const {done, value} = await reader.read();
                if (done) break;

                // Декодируем и чистим лишние "data:"
                const chunk = decoder.decode(value).replace(/^data:\s*/g, "");
                assistantMessage += chunk;

                setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1].content = assistantMessage;
                    return updated;
                });
            }
        } catch {
            setMessages((prev) => [...prev, {role: "assistant", content: "Ошибка соединения"}]);
        }

        setLoading(false);
    };

    return (
        <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
            {/* Чат */}
            <div className="w-full max-w-2xl bg-white p-4 rounded shadow flex flex-col gap-2 overflow-y-auto flex-1">
                {messages.map((m, i) => (
                    <div
                        key={i}
                        className={`p-2 rounded max-w-[80%] break-words ${
                            m.role === "user" ? "bg-blue-100 self-end" : "bg-green-100 self-start"
                        }`}
                    >
                        {m.content}
                    </div>
                ))}
                {loading && (
                    <div className="bg-gray-200 p-2 rounded self-start animate-pulse">
                        Печатает...
                    </div>
                )}
                <div ref={bottomRef}></div>
            </div>

            {/* Инпут */}
            <div className="flex w-full max-w-2xl mt-2">
                <input
                    className="flex-1 p-2 border rounded"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                    placeholder="Введите сообщение..."
                />
                <button className="ml-2 p-2 bg-blue-500 text-white rounded" onClick={sendMessage}>
                    Send
                </button>
            </div>
        </div>
    );
}