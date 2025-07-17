from dotenv import load_dotenv
# load all the environemnt variables
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content([prompt + question])
    return response.text

# Fucntion To retrieve query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_database_info():
    conn = sqlite3.connect("database.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = []
    for table in tables:
        table_name = table[0]
        cursor.execute("PRAGMA table_info(?)", (table_name,)) # Use ? for parameter binding which is more secure
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        schema_info.append(f"Table: {table_name}, Columns: {', '.join(column_names)}")
    
    conn.close()
    return "\n".join(schema_info)

schema_text = get_database_info()

prompt = f"""
You are an expert SQL developer with deep knowledge of SQLite and soccer/football analytics.
You understand both the technical aspects of database queries and the domain knowledge of football/soccer.

This is a soccer/football database containing player statistics, match results, and team performance data.

The database has the following tables and columns:
{schema_text}

CRITICAL INSTRUCTIONS:
1. Convert the users question into a valid SQLite SQL query
2. Only output the SQL query - no explanations, markdown, or formatting
3. Do not include ```sql or ``` in the output
4. Use exact table and column names from the schema above

SQLite-SPECIFIC RULES:
- Use ROUND(value, 2) for decimal precision
- Use IS NOT NULL instead of != NULL  
- Use || for string concatenation (not CONCAT)
- Use COALESCE() for handling NULL values
- For averages: (col1 + col2 + col3) /3 AVG with multiple columns)
- Use .0 division to ensure floating-point results

COMMON QUERY PATTERNS:
- Player attributes: JOIN Player with Player_Attributes on player_api_id
- Top performers: ORDER BY attribute DESC LIMIT N

ERROR HANDLING:
- If question cannot be answered with available data, return: SELECT 'Cannot answer with available data' as result
- If question is unclear, ask for clarification in SQL comment: -- Please clarify your question
- Do not generate invalid SQL syntax

Remember: This is SQLite, not MySQL or PostgreSQL. Follow SQLite syntax rules strictly.
"""

# Streamlit App
st.set_page_config(page_title="Text to SQL Query Generator using Gemini")
st.header("Ask questions about your database")

# Input the question
question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")
if submit and question:
    try:
        sql_query = get_gemini_response(question, prompt)
        results = read_sql_query(sql_query, "database.sqlite")
        st.subheader("The Response is:")
        st.dataframe(results)
    except Exception as e:
        st.error(f"Error: {str(e)}")
