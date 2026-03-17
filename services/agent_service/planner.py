# services/agent_service/planner.py

import httpx
import json
from services.agent_service.prompt import PLANNER_PROMPT
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("Planner"), {})

LLM_URL = "http://localhost:8100/chat"


async def create_plan(user_message: str):
    prompt = PLANNER_PROMPT + "\n\nUser:\n" + user_message

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            r = await client.post(LLM_URL, json={"message": prompt})
        except Exception as e:
            logger.error(f"Planner HTTP error: {e}")
            return []

        if r.status_code != 200:
            logger.error(f"Planner ERROR {r.status_code}: {r.text}")
            return []

        data = r.json()
        answer = data.get("answer", "").strip()

    try:
        parsed = json.loads(answer)
        steps = parsed.get("steps", [])
        logger.info(f"PLAN: {steps}")
        return steps
    except Exception as e:
        logger.error(f"Planner parse error: {e}")
        return []