from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def get_schema()->str:
    # fetch db schema to inject into LLM prompt
    query="""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position;
    """

    # information_schema.columns 

    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows=result.fetchall()


    schema_str = ""
    current_table = None
    for table, column, dtype in rows:
        if table != current_table:
            schema_str += f"\nTable: {table}\n"
            current_table = table
        schema_str += f"  - {column} ({dtype})\n"

    return schema_str

def run_query(sql: str) -> list[dict]:
    """Execute a SQL query and return results as a list of dicts."""
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()

    serialized = []
    for row in rows:
        serialized_row = {}
        for col, val in zip(columns, row):
            if hasattr(val, '__float__'):
                serialized_row[col] = float(val)
            elif val is None:
                serialized_row[col] = None
            else:
                serialized_row[col] = val
        serialized.append(serialized_row)

    return serialized