from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict
from db.connection import get_schema, run_query
from agent.prompts import SYSTEM_PROMPT, FORMAT_PROMPT
from agent.tools import detect_chart
from dotenv import load_dotenv
import os

load_dotenv()

# State 
class AgentState(TypedDict):
    question: str
    schema: str
    sql: str
    results: list[dict]
    answer: str
    chart: dict
    error: str
    retry_count: int

# LLM 

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Nodes
def schema_context_node(state: AgentState) -> AgentState:
    """Fetch schema from PostgreSQL and store in state."""
    schema = get_schema()
    return {**state, "schema": schema}


def sql_generate_node(state: AgentState) -> AgentState:
    """LLM reads question + schema and generates SQL."""
    system_msg = SystemMessage(
        content=SYSTEM_PROMPT.format(schema=state["schema"])
    )
    human_msg = HumanMessage(content=state["question"])

    # If retrying, add error context
    if state.get("error"):
        human_msg = HumanMessage(
            content=f"""
            Question: {state["question"]}
            
            Your previous SQL failed with this error:
            {state["error"]}
            
            Please fix the SQL and try again.
            """
        )

    response = llm.invoke([system_msg, human_msg])
    sql = response.content.strip()

    return {**state, "sql": sql, "error": ""}


def sql_execute_node(state: AgentState) -> AgentState:
    """Run the generated SQL against PostgreSQL."""
    try:
        results = run_query(state["sql"])
        return {
            **state,
            "results": results,
            "error": ""
        }
    except Exception as e:
        return {
            **state,
            "results": [],
            "error": str(e),
            "retry_count": state.get("retry_count", 0) + 1
        }


def format_answer_node(state: AgentState) -> AgentState:
    """LLM formats raw results into a natural language answer."""
    prompt = FORMAT_PROMPT.format(
        question=state["question"],
        results=state["results"]
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "answer": response.content.strip()}


def chart_node(state: AgentState) -> AgentState:
    """Detect if results are chartable and return chart config."""
    chart_result = detect_chart.invoke({"data": state["results"]})
    return {**state, "chart": chart_result}


# Routing 
def should_retry(state: AgentState) -> str:
    """Decide whether to retry SQL generation or proceed."""
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "retry"
    return "proceed"


# Graph
def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("schema_context", schema_context_node)
    graph.add_node("sql_generate", sql_generate_node)
    graph.add_node("sql_execute", sql_execute_node)
    graph.add_node("format_answer", format_answer_node)
    graph.add_node("chart", chart_node)

    # Add edges
    graph.set_entry_point("schema_context")
    graph.add_edge("schema_context", "sql_generate")
    graph.add_edge("sql_generate", "sql_execute")

    # Conditional edge — retry or proceed
    graph.add_conditional_edges(
        "sql_execute",
        should_retry,
        {
            "retry": "sql_generate",
            "proceed": "format_answer"
        }
    )

    graph.add_edge("format_answer", "chart")
    graph.add_edge("chart", END)

    return graph.compile()


agent = build_graph()