import streamlit as st
import sqlite3
import os
import pandas as pd
import sys
import re

# Append the path to the parent directory of InfoMatching_Team3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../InfoMatching_Team3')))
from resume_interface import read_resume

def sanitize_column_name(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

def main():
    st.title("Job Description Page")

    with st.sidebar:
        st.header("Upload Job Descriptions")
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(job_description)")
    column_names = [info[1] for info in cursor.fetchall()]

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        for index, row in df.iterrows():
            extracted_data = extract_job_data(row['job_description'])
            data = {
                'id': row['id'],
                'job_company': row['job_company'],
                'job_title': row['job_title'],
                'job_description': row['job_description'],
                'job_application_url': row['job_application_url'],
                **{sanitize_column_name(k): (', '.join(map(str, v)) if isinstance(v, list) else v) for k, v in extracted_data.items()}
            }
            cursor.execute("SELECT COUNT(*) FROM job_description WHERE id = ?", (row['id'],))
            count = cursor.fetchone()[0]
            if count == 0:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                cursor.execute(f'INSERT INTO job_description ({columns}) VALUES ({placeholders})', list(data.values()))
            else:
                update_columns = ', '.join([f"{key} = ?" for key in data.keys()])
                cursor.execute(f'UPDATE job_description SET {update_columns} WHERE id = ?', list(data.values()) + [row['id']])
        connection.commit()
        st.success("Job descriptions uploaded successfully!")
    
    with st.sidebar:
        st.header("Filters")
        filter_columns = [col for col in column_names if col not in ['job_application_url']]
        selected_columns = st.multiselect("Display columns", options=filter_columns, default=filter_columns)
        query = "SELECT * FROM job_description WHERE 1=1"
        params = []
        for column in filter_columns:
            filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
            if filter_input:
                query += f" AND {column} LIKE ?"
                params.append(f"%{filter_input}%")
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    connection.close()

    if data:
        df = pd.DataFrame(data, columns=column_names)
        df.insert(0, "Select", False)
        edited_df = st.data_editor(
            df, 
            column_config={
                "id": st.column_config.NumberColumn("ID"),
                "job_title": st.column_config.TextColumn("Job Title"),
                "job_company": st.column_config.TextColumn("Company"),
                "Select": st.column_config.CheckboxColumn("Select")
            },
            hide_index=True
        )
        selected_files = [f"{row['job_company']}: {row['job_title']}" for _, row in edited_df.iterrows() if row["Select"]]
        selected_ids = edited_df[edited_df["Select"] == True]["id"].tolist()
        st.write("Selected Jobs:", selected_files)
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        if "jobs_to_delete" not in st.session_state:
            st.session_state.jobs_to_delete = []
        if st.button("Delete Selected"):
            if selected_ids:
                st.session_state.confirm_delete = True
                st.session_state.jobs_to_delete = selected_ids
                st.rerun()
        if st.session_state.confirm_delete:
            st.warning("Are you sure you want to delete the selected job descriptions?")
            if st.button("Confirm Delete"):
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                for job_id in st.session_state.jobs_to_delete:
                    cursor.execute("DELETE FROM job_description WHERE id = ?", (job_id,))
                connection.commit()
                connection.close()
                st.success("Selected job descriptions deleted successfully!")
                st.session_state.confirm_delete = False
                st.session_state.jobs_to_delete = []
                st.rerun()

if __name__ == "__main__":
    main()
