import {useEffect, useRef, useState} from "react";
import ReactMarkdown from "react-markdown";

export default function ChatInterface() {

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({behavior: "smooth"});
    }, [messages]);

    async function sendMessage() {

        if (!input.trim()) return;

        const userMessage = input;

        setMessages(prev => [
            ...prev,
            {role: "user", content: userMessage},
            {role: "ai", content: ""}
        ]);

        setInput("");

        try {

            const response = await fetch("http://localhost:8500/chat_stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let aiText = "";

            while (true) {

                const {done, value} = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);

                aiText += chunk;

                setMessages(prev => {

                    const updated = [...prev];

                    updated[updated.length - 1] = {
                        role: "ai",
                        content: aiText
                    };

                    return updated;

                });

            }

        } catch (err) {

            setMessages(prev => {

                const updated = [...prev];

                updated[updated.length - 1] = {
                    role: "ai",
                    content: "Connection error"
                };

                return updated;

            });

        }

    }

    function handleKey(e) {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            sendMessage();

        }

    }

    return (

        <div style={{
            border: "1px solid #ddd",
            borderRadius: "10px",
            background: "white",
            height: "80vh",
            display: "flex",
            flexDirection: "column"
        }}>

            <div style={{
                flex: 1,
                overflowY: "auto",
                padding: "20px"
            }}>

                {messages.map((m, i) => (

                    <div key={i}
                         style={{
                             background: m.role === "user" ? "#cce5ff" : "#f1f1f1",
                             padding: "10px",
                             borderRadius: "10px",
                             marginBottom: "10px",
                             maxWidth: "70%",
                             marginLeft: m.role === "user" ? "auto" : "0"
                         }}
                    >

                        <ReactMarkdown>
                            {m.content}
                        </ReactMarkdown>

                    </div>

                ))}

                <div ref={bottomRef}></div>

            </div>

            <div style={{
                borderTop: "1px solid #ddd",
                padding: "10px",
                display: "flex",
                gap: "10px"
            }}>

        <textarea
            rows={2}
            style={{
                flex: 1,
                padding: "10px"
            }}
            placeholder="Введите сообщение..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
        />

                <button
                    onClick={sendMessage}
                    style={{
                        padding: "10px 20px"
                    }}
                >
                    Send
                </button>

            </div>

        </div>

    );

}