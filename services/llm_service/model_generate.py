from llama_cpp import Llama

MODEL_PATH = "models/qwen2.5-7b-instruct-q4_k_m.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=35
)


def model_generate(message: str):
    prompt = "<|im_start|>system\n"
    prompt += "Ты полезный AI-ассистент. Всегда отвечай только на русском языке. "
    prompt += "Не используй английский или китайский. Отвечай кратко и понятно.\n"
    prompt += "<|im_end|>\n"

    output = llm(
        prompt,
        max_tokens=200,
        temperature=0.6,
        stop=["User:"]
    )

    return output["choices"][0]["text"].strip()
