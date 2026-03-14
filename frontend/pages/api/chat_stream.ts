import type {NextApiRequest, NextApiResponse} from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== "POST") return res.status(405).json({error: "Method not allowed"});

    const {message} = req.body;
    if (!message) return res.status(400).json({error: "Message required"});

    try {
        const response = await fetch("http://localhost:8000/chat_stream", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message}),
        });

        if (!response.body) return res.status(500).end();

        res.setHeader("Content-Type", "text/event-stream");
        res.setHeader("Cache-Control", "no-cache");
        res.setHeader("Connection", "keep-alive");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            // Отбрасываем лишние строки, пропускаем только data:
            const lines = chunk.split("\n");
            for (let line of lines) {
                line = line.trim();
                if (!line) continue;
                res.write(line);
            }
        }

        res.end();
    } catch (e) {
        res.status(500).json({error: "Gateway connection error"});
    }
}