import subprocess
import sys
import time

services = [
    ("LLM Service", "services.llm_service.main:app", 8100),
    ("RAG Service", "services.rag_service.main:app", 8200),
    ("Document Service", "services.document_service.main:app", 8300),
    ("Math Service", "services.math_service.main:app", 8400),
    ("Gateway", "services.gateway_service.main:app", 8000),
]

processes = []

print("\n🚀 Starting AI Platform v5...\n")

for name, module, port in services:
    print(f"Starting {name} on port {port}")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        module,
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--reload"
    ]

    p = subprocess.Popen(cmd)
    processes.append(p)

    time.sleep(1)

print("\n✅ All services started\n")
print("Gateway: http://localhost:8000")
print("LLM:     http://localhost:8100")
print("RAG:     http://localhost:8200")
print("Docs:    http://localhost:8300")
print("Math:    http://localhost:8400")

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n🛑 Stopping services...")
    for p in processes:
        p.terminate()
