from fastapi import FastAPI
from .schemas import MathRequest, MathResponse
from .engine import solve_expression

app = FastAPI(title="Math Tool Service", version="v1")


@app.post("/solve", response_model=MathResponse)
def solve_math(req: MathRequest):
    result = solve_expression(req.expression)
    return MathResponse(result=result)


@app.get("/health")
def health_check():
    return {"status": "ok"}
