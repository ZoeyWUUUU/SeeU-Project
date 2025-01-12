# pages/1_Resume.py

import streamlit as st
import sqlite3
import os
import pandas as pd

def main():
    st.title("Resume Page")

    # Add a text input for the student name
    student_name = st.text_input("Enter Student Name to Filter Results")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # cursor.execute("SELECT * FROM uploads")

    # Build the query based on search criteria
    if student_name:
        cursor.execute("SELECT * FROM uploads WHERE student_name LIKE ?", ('%' + student_name + '%',))
    else:
        cursor.execute("SELECT * FROM uploads")

    data = cursor.fetchall()

    # Fetch column names
    cursor.execute("PRAGMA table_info(uploads)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    connection.close()

    if data:
        st.subheader("Resume Table Data")
        df = pd.DataFrame(data, columns=column_names)
        # st.table(data)
        # st.table(df)
        
        # # Convert file_path to clickable links
        # df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{x}" download>{os.path.basename(x)}</a>')
                # Convert file_path to clickable links
        # uploads_dir = os.path.join(script_dir, "../../uploads")
        # df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{os.path.join(uploads_dir, os.path.basename(x))}" download>{os.path.basename(x)}</a>')
        # Convert file_path to clickable links
        server_url = "http://localhost:8000"
        df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{server_url}/{os.path.basename(x)}" download>{os.path.basename(x)}</a>')
        
        # Display the DataFrame with clickable links
        st.write(df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.write("No resumes found in the database.")

if __name__ == "__main__":
    main()
