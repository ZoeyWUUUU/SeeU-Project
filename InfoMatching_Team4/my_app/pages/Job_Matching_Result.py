# pages/3_Job_Matching_Result.py

import streamlit as st
import sqlite3
import os
import pandas as pd

def main():
    st.title("Job Matching Result Page")

    # Add a text input for the student name
    student_name = st.text_input("Enter Student Name to Filter Results")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    if student_name:
        cursor.execute("SELECT * FROM job_matching_result WHERE student_name = ?", (student_name,))
    else:
        cursor.execute("SELECT * FROM job_matching_result")
    
    # cursor.execute("SELECT * FROM job_matching_result")
    data = cursor.fetchall()

    # Fetch column names
    cursor.execute("PRAGMA table_info(job_matching_result)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    connection.close()

    if data:
        st.subheader("Job Matching Result Table Data")
        df = pd.DataFrame(data, columns=column_names)
        # st.table(data)
        st.table(df)
    else:
        st.write("No matching results found.")

if __name__ == "__main__":
    main()
