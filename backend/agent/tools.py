from langchain_core.tools import tool
from db.connection import run_query
import pandas as pd

@tool
def execute_sql(sql:str)->dict:
    """Execute a query against the database and return results."""
    try:
        result = run_query(sql)
        return {
            "success": True,
            "data": results,
            "row_count": len(results)
        }
    except Exception as e:
        return{
            "success": False,
            "error": str(e),
            "data": []
        }

@tool
def detect_chart(data: list[dict]) -> dict:
    """Detect if the query result is chartable and suggest chart type."""
    if not data:
        return {"chartable": False, "reason": "No data"}

    df = pd.DataFrame(data)
    columns = df.columns.tolist()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(include="object").columns.tolist()


    if not numeric_cols or not text_cols:
        return {"chartable": False, "reason": "Need both text and numeric columns"}

    if len(df) <= 10:
        chart_type = "bar"
    else:
        chart_type = "line"

    return {
          "chartable": True,
        "chart_type": chart_type,
        "x_axis": text_cols[0],
        "y_axis": numeric_cols[0],
        "data": data
    }

