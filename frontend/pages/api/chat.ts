import type {NextApiRequest, NextApiResponse} from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({error: "Method not allowed"});

  const {message} = req.body;
  if (!message) return res.status(400).json({error: "Message required"});

  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message})
    });

    const data = await response.json();
    return res.status(200).json({answer: data.answer});
  } catch {
    return res.status(500).json({answer: "Gateway connection error"});
  }
}