from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graph import agent

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sql-data-analyst-agent.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sql: str
    chart: dict
    row_count: int



@app.get("/")
def health_check():
    return {"status": "ok", "message": "SQL Analyst Agent is running"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    # Initial state
    initial_state = {
        "question": request.question,
        "schema": "",
        "sql": "",
        "results": [],
        "answer": "",
        "chart": {},
        "error": "",
        "retry_count": 0
    }

    # Run the agent
    final_state = await agent.ainvoke(initial_state)

    return QueryResponse(
        answer=final_state["answer"],
        sql=final_state["sql"],
        chart=final_state["chart"],
        row_count=len(final_state["results"])
    )