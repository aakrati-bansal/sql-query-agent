from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def run_query_agent(question, db_name):
    db = SQLDatabase.from_uri(f"sqlite:///{db_name}")
    schema = db.get_table_info()
    max_retries = 3
    attempt = 0
    previous_attempt = ""

    while attempt < max_retries:
        sql_prompt = f"""You are a SQL expert working with a SQLite database.

Database schema:
{schema}

User question: {question}

Rules:
- Write the SIMPLEST possible SQL query that answers the question
- Always include the FROM clause with the correct table name from the schema
- Use only standard SQLite syntax
- Never use parameters like ?, :param or $1 — use actual values only
- For simple questions like "max", "min", "total", "count" — use simple aggregations
- Only add LIMIT 100 when returning multiple rows
- Never add WHERE clauses unless the user specifically asks to filter
- Return ONLY the SQL query, nothing else, no explanation
- Column names with spaces must be wrapped in backticks like `Order Date`
- To filter by year use: strftime('%Y', `Order Date`) = '2023'
- Never use YEAR(), NOW() or any MySQL functions — SQLite only
- Dates are stored in ISO format YYYY-MM-DD
- To filter by year use: strftime('%Y', "Order Date") = '2023'

{previous_attempt}
"""
        response = llm.invoke(sql_prompt)
        sql_query = response.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        print(f"--- Attempt {attempt + 1} ---")
        print(f"SQL Query: {sql_query}")

        try:
            result = db.run(sql_query)
            break
        except Exception as e:
            attempt += 1
            previous_attempt = f"Your previous query was: {sql_query}. It failed with this error: {str(e)}. Please fix it."
            print(f"Error: {str(e)}")
            continue
    else:
        return "Could not generate a valid query after 3 attempts."

    if len(str(result)) > 2000:
        result = str(result)[:2000] + "... [truncated]"

    output_prompt = f"""You are an expert at explaining SQL query results in plain English.
You have:
- User question: {question}
- SQL query that was run: {sql_query}
- Result from the database: {result}

Write a clear, concise answer to the user's question based on the result.
Format your response exactly like this:
Answer: [plain english answer here]
SQL Query: [the sql query here]
"""
    response2 = llm.invoke(output_prompt)
    return response2.content.strip()