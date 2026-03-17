import json
import httpx

LLM_URL = "http://localhost:8100/chat"


async def create_plan(user_message):

    prompt = f"""
You are an AI planner.

Break the user task into steps.

Return JSON:

{{
 "steps":[
  {{"tool":"tool_name","args":{{}}}}
 ]
}}

User task:
{user_message}
"""

    async with httpx.AsyncClient(timeout=120) as client:

        r = await client.post(
            LLM_URL,
            json={"message": prompt}
        )

    data = r.json()

    text = data.get("answer", "")

    try:
        plan = json.loads(text)
    except:
        plan = {"steps": []}

    return plan