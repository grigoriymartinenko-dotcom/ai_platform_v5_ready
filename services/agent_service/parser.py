# services/agent_service/parser.py

import json

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("Parser"), {})

def extract_json_objects(text: str):
    objects = []
    stack = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if stack == 0:
                start = i
            stack += 1
        elif ch == "}":
            stack -= 1
            if stack == 0 and start is not None:
                objects.append(text[start:i + 1])
                start = None
    return objects

def parse_llm_output(text: str):
    results = []
    text = text.strip()

    if text.startswith("[") and text.endswith("]"):
        try:
            data_list = json.loads(text)
            for data in data_list:
                if not isinstance(data, dict):
                    continue
                if "tool" in data:
                    args = data.get("args", {})
                    if not isinstance(args, dict):
                        args = {}
                    results.append({"type": "tool", "tool": data["tool"], "args": args})
                if "final" in data:
                    results.append({"type": "final", "content": data["final"]})
            if results:
                return results
        except Exception:
            pass

    json_blocks = extract_json_objects(text)
    for block in json_blocks:
        try:
            data = json.loads(block)
        except Exception:
            continue
        if "tool" in data:
            args = data.get("args", {})
            if not isinstance(args, dict):
                args = {}
            results.append({"type": "tool", "tool": data["tool"], "args": args})
        if "final" in data:
            results.append({"type": "final", "content": data["final"]})

    if not results:
        results.append({"type": "final", "content": text.strip()})

    return results