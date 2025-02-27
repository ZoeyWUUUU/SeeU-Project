import streamlit as st
import sqlite3
import os
import pandas as pd
import sys
import re

# Append the path to the parent directory of InfoMatching_Team2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../InfoMatching_Team2')))
from jd_function import extract_job_data


def sanitize_column_name(name):
    return re.sub(r'\W|^(?=\d)', '_', name).lower()

def main():
    st.markdown("<h1 style='font-size:24px;'>Job Description</h1>", unsafe_allow_html=True)

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
                'job_company': row['job_company'],
                'job_title': row['job_title'],
                'job_description': row['job_description'],
                'job_application_url': row['job_application_url'],
                **{sanitize_column_name(k): (', '.join(map(str, v)) if isinstance(v, list) else v) for k, v in extracted_data.items()}
            }

            # Ensure all necessary columns exist in the database
            cursor.execute("PRAGMA table_info(job_description)")
            existing_columns = {info[1].lower() for info in cursor.fetchall()}
            new_columns = {sanitize_column_name(col) for col in data.keys()} - existing_columns
            
            for column in new_columns:
                cursor.execute(f"ALTER TABLE job_description ADD COLUMN {column} TEXT")
                column_names.append(column)

            cursor.execute("SELECT COUNT(*) FROM job_description WHERE job_company = ? AND job_title = ?", (row['job_company'], row['job_title']))
            count = cursor.fetchone()[0]
            if count == 0:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                cursor.execute(f'INSERT INTO job_description ({columns}) VALUES ({placeholders})', list(data.values()))
            else:
                update_columns = ', '.join([f"{key} = ?" for key in data.keys()])
                cursor.execute(f'UPDATE job_description SET {update_columns} WHERE job_company = ? AND job_title = ?', list(data.values()) + [row['job_company'], row['job_title']])
        connection.commit()
        st.success("Job descriptions uploaded successfully!")
    
    with st.sidebar:
        st.header("Filters")
        essential_columns = ['job_company', 'job_title']
        filter_columns = [col for col in column_names if col not in ['job_application_url']]
        selectable_columns = [col for col in filter_columns if col not in essential_columns]
        selected_columns = st.multiselect("Display columns", options=selectable_columns, default=selectable_columns if selectable_columns else [])
        query = "SELECT " + ', '.join(column_names) + " FROM job_description WHERE 1=1"
        params = []
        for column in filter_columns:
            filter_input = st.text_input(f"{column}", key=column)
            if filter_input:
                query += f" AND {column} LIKE ?"
                params.append(f"%{filter_input}%")
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    connection.close()

    if data:
        df = pd.DataFrame(data, columns=column_names)
        display_columns = essential_columns + selected_columns  # Ensure essential columns are always included
        df = df[display_columns]
        df.insert(0, "Select", False)
        edited_df = st.data_editor(
            df, 
            column_config={
                "job_title": st.column_config.TextColumn("Job Title", help="Job position"),
                "job_company": st.column_config.TextColumn("Company", help="Company name"),
                "Select": st.column_config.CheckboxColumn("Select")
            },
            hide_index=True
        )
        selected_files = [f"{row['job_company']}: {row['job_title']}" for _, row in edited_df.iterrows() if row["Select"]]
        st.write("Selected Jobs:", selected_files)
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        if "jobs_to_delete" not in st.session_state:
            st.session_state.jobs_to_delete = []
        if st.button("Delete Selected"):
            if selected_files:
                st.session_state.confirm_delete = True
                st.session_state.jobs_to_delete = selected_files
                st.rerun()
        if st.session_state.confirm_delete:
            st.warning("Are you sure you want to delete the selected job descriptions?")
            if st.button("Confirm Delete"):
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                for job in st.session_state.jobs_to_delete:
                    company, title = job.split(": ")
                    cursor.execute("DELETE FROM job_description WHERE job_company = ? AND job_title = ?", (company, title))
                connection.commit()
                connection.close()
                st.success("Selected job descriptions deleted successfully!")
                st.session_state.confirm_delete = False
                st.session_state.jobs_to_delete = []
                st.rerun()

if __name__ == "__main__":
    main()
