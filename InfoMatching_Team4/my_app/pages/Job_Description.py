# pages/2_Job_Description.py

import streamlit as st
import sqlite3
import os
import pandas as pd

def main():
    st.title("Job Description Page")

    # Add text inputs for search criteria
    company_name = st.text_input("Enter Company Name to Filter Results")
    job_title = st.text_input("Enter Job Title to Filter Results")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # cursor.execute("SELECT * FROM job_description")
    
    # Build the query based on search criteria
    query = "SELECT * FROM job_description WHERE 1=1"
    params = []

    if company_name:
        query += " AND job_company LIKE ?"
        params.append(f"%{company_name}%")

    if job_title:
        query += " AND job_title LIKE ?"
        params.append(f"%{job_title}%")

    cursor.execute(query, params)
    
    data = cursor.fetchall()

    # Fetch column names
    cursor.execute("PRAGMA table_info(job_description)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    connection.close()

    if data:
        st.subheader("Job Description Table Data")
        df = pd.DataFrame(data, columns=column_names)
        # st.table(data)
        st.table(df)
    else:
        st.write("No job descriptions found.")

if __name__ == "__main__":
    main()
