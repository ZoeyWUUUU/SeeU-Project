# pages/1_Resume.py

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
    # Replace spaces and special characters with underscores
    return re.sub(r'\W|^(?=\d)', '_', name)

def main():
    st.subheader("Resume Page")

    # # Add a text input for the new student name
    # new_student_name = st.text_input("Enter Student Name")
    # new_uploaded_resume = st.file_uploader("Upload Resume for Student")
    # Add a file uploader for the resume
    # uploaded_resumes = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True)

    # Move the file uploader to the sidebar
    with st.sidebar:
        # st.header("Upload Resumes")
        # Add a file uploader for the resume
        uploaded_resumes = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True)

    if uploaded_resumes:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "../../", "my_database.db")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Get existing columns in the uploads table
        cursor.execute("PRAGMA table_info(uploads)")
        existing_columns = [info[1] for info in cursor.fetchall()]

        for uploaded_resume in uploaded_resumes:
            # Extract information from the resume
            extracted_data = read_resume(file_object=uploaded_resume)

            # Add new columns to the uploads table based on the extracted data keys
            for key in extracted_data.keys():
                sanitized_key = sanitize_column_name(key)
                if sanitized_key not in existing_columns:
                    cursor.execute(f"ALTER TABLE uploads ADD COLUMN {sanitized_key} TEXT")
                    existing_columns.append(sanitized_key)

            # Prepare the data for insertion
            data = {
                'file_name': uploaded_resume.name,
                'file_path': os.path.join("uploads", uploaded_resume.name),
                **{sanitize_column_name(k): (', '.join(map(str, v)) if isinstance(v, list) else v) for k, v in extracted_data.items()}
            }

            # Save the uploaded file to the 'uploads' directory
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
            save_path = os.path.join(upload_dir, uploaded_resume.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_resume.getbuffer())

            # Check if the file already exists in the database
            cursor.execute("SELECT COUNT(*) FROM uploads WHERE file_name = ?", (uploaded_resume.name,))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert a new entry into the database
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                cursor.execute(f'''
                    INSERT INTO uploads ({columns})
                    VALUES ({placeholders})
                ''', list(data.values()))
            else:
                # Update the existing entry in the database
                update_columns = ', '.join([f"{key} = ?" for key in data.keys()])
                cursor.execute(f'''
                    UPDATE uploads
                    SET {update_columns}
                    WHERE file_name = ?
                ''', list(data.values()) + [uploaded_resume.name])

        connection.commit()
        connection.close()

        st.success("Resumes uploaded successfully!")
    # if new_student_name and new_uploaded_resume:
    #     # Save the uploaded file to the 'uploads' directory
    #     upload_dir = "uploads"
    #     os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
    #     save_path = os.path.join(upload_dir, new_uploaded_resume.name)
    #     with open(save_path, "wb") as f:
    #         f.write(new_uploaded_resume.getbuffer())

    #     # Check if the student name already exists
    #     script_dir = os.path.dirname(os.path.abspath(__file__))
    #     db_path = os.path.join(script_dir, "../../", "my_database.db")
    #     connection = sqlite3.connect(db_path)
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT COUNT(*) FROM uploads WHERE student_name = ?", (new_student_name,))
    #     count = cursor.fetchone()[0]

    #     if count > 0:
    #         # Update the existing entry
    #         cursor.execute('''
    #             UPDATE uploads
    #             SET file_name = ?, file_path = ?, uploaded_at = CURRENT_TIMESTAMP
    #             WHERE student_name = ?
    #         ''', (new_uploaded_resume.name, save_path, new_student_name))
    #     else:
    #         # Insert a new entry
    #         cursor.execute('''
    #             INSERT INTO uploads (student_name, file_name, file_path)
    #             VALUES (?, ?, ?)
    #         ''', (new_student_name, new_uploaded_resume.name, save_path))

    #     connection.commit()
    #     connection.close()

    #     st.success(f"New resume for {new_student_name} uploaded successfully!")


    # # Add a text input for the student name
    # student_name_filter = st.text_input("Enter Student Name to Filter Results")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Fetch column names
    cursor.execute("PRAGMA table_info(uploads)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    # Build the query based on search criteria
    query = "SELECT * FROM uploads WHERE 1=1"
    params = []
    # if student_name_filter:
    #     query += " AND student_name LIKE ?"
    #     params.append(f"%{student_name_filter}%")

    # Add filters to the sidebar
    with st.sidebar:
        # st.header("Filters")
        filter_columns = [col for col in column_names if col != 'file_path']
        
        # Add a multiselect widget for selecting columns to display
        # st.write("Select columns to display:")
        selected_columns = st.multiselect("Display columns", options=filter_columns, default=filter_columns)

        # Add text input filters for each column
        # for column in selected_columns:
        for column in filter_columns:
            if column not in st.session_state:
                st.session_state[column] = ""
            filter_input = st.text_input(f"Filter {column} (case insensitive)", value=st.session_state[column], key=column)
            # filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
            if filter_input:
                query += f" AND {column} LIKE ?"
                params.append(f"%{filter_input}%")

        # Add buttons to apply and clear filters side by side
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.write("Click to apply all filters")
            apply_filter = st.button("Apply filter")
        with col2:
            st.write("Double click to clear ALL filter")
            clear_filter = st.button("Clear all filters")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.write("Click to see full table")
            cancel_filter = st.button("Cancel filter")
        with col2:
            st.write("After clearing, click to restart filter")
            restart_filter = st.button("Restart filter")

    # Execute the query with the filters
    if cancel_filter:
        query = "SELECT * FROM uploads"
        params = []

    cursor.execute(query, params)
    data = cursor.fetchall()
    connection.close()

    if data:
        # st.subheader("Resume Table Data")
        df = pd.DataFrame(data, columns=column_names)
        
        # Convert file_path to clickable links
        # server_url = "http://localhost:8000"
        server_url = "http://localhost:8000"
        # df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{server_url}/{os.path.basename(x)}" download>{os.path.basename(x)}</a>')
        df['file_name'] = df.apply(lambda row: f'<a href="{server_url}/{row["file_name"]}" target="_blank">{row["file_name"]}</a>', axis=1)

        # Add checkboxes for selecting files to delete
        # df['select'] = df.apply(lambda row: st.checkbox(f"Select {row['file_name']}", key=row['file_name']), axis=1)
        # df.insert(0, 'select', df.apply(lambda row: st.checkbox(f"Select {row['file_name']}", key=row['file_name']), axis=1))
        # df.insert(0, 'select', df.apply(lambda row: st.checkbox("",key=row['file_name']), axis=1))


        # Display the DataFrame with clickable links
        if apply_filter:
            # Execute the query with the filters
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(query, params)
            filtered_data = cursor.fetchall()
            connection.close()

            # Convert the filtered data to a DataFrame
            filtered_df = pd.DataFrame(filtered_data, columns=column_names)
            filtered_df['file_name'] = filtered_df.apply(lambda row: f'<a href="{server_url}/{row["file_name"]}" target="_blank">{row["file_name"]}</a>', axis=1)
            filtered_df['select'] = filtered_df.apply(lambda row: st.checkbox("", key=row['file_name']), axis=1)

            if filtered_df.empty:
                st.write("No result")
            else:
                # st.markdown(filtered_df[['select'] + selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
                st.markdown(filtered_df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)

                # st.markdown(filtered_df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
        elif clear_filter:
            # Clear the filters by resetting the session state
            for column in filter_columns:
                if column in st.session_state:
                    del st.session_state[column]

            # Display the full DataFrame based on selected columns
            st.markdown(df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
            # st.markdown(df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            # Display the full DataFrame based on selected columns if no filter is applied
            st.markdown(df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
            # st.markdown(df[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # cursor.execute("SELECT * FROM uploads")

    # Build the query based on search criteria
    # if student_name_filter:
    #     cursor.execute("SELECT * FROM uploads WHERE student_name LIKE ?", ('%' + student_name_filter + '%',))
    # else:
    #     cursor.execute("SELECT * FROM uploads")

    # cursor.execute("SELECT * FROM uploads")

    # Build the query based on search criteria
    # if student_name_filter:
    #     cursor.execute("SELECT * FROM uploads WHERE student_name LIKE ?", ('%' + student_name_filter + '%',))
    # else:
    #     cursor.execute("SELECT * FROM uploads")

    # data = cursor.fetchall()

    # Fetch column names
    # cursor.execute("PRAGMA table_info(uploads)")
    # columns_info = cursor.fetchall()
    # column_names = [info[1] for info in columns_info]

    # connection.close()

    # if data:
    #     # st.subheader("Resume Table Data")
    #     df = pd.DataFrame(data, columns=column_names)
        
    #     # Convert file_path to clickable links
    #     server_url = "http://localhost:8000"
    #     df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{server_url}/{os.path.basename(x)}" download>{os.path.basename(x)}</a>')
        
    #     # Display the DataFrame with clickable links
    #     st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # # Create two columns
        # col1, col2 = st.columns([2, 1])
        
        # with col1:
        #     # Display the DataFrame with clickable links and set table width
        #     st.write(df.to_html(escape=False, index=False, justify='left'), unsafe_allow_html=True)
        #     st.markdown(
        #         """
        #         <style>
        #         table {
        #             width: 75% !important;
        #         }
        #         </style>
        #         """,
        #         unsafe_allow_html=True
        #     )
        
        # with col2:

        #     # # Add custom CSS to adjust the size of the file uploader widget
        #     # st.markdown(
        #     #     """
        #     #     <style>
        #     #     .stFileUpload {
        #     #         height: 10px;
        #     #         width: 10px;
        #     #     }
        #     #     </style>
        #     #     """,
        #     #     unsafe_allow_html=True,
        #     #     # scope="file_uploader"
        #     # )
        #      # Add custom CSS to adjust the size and style of the file uploader widget
        #     st.markdown(
        #         """
        #         <style>
        #         .stFileUpload label {
        #             font-size: 14px;
        #             color: blue;
        #         }
        #         </style>
        #         """,
        #         unsafe_allow_html=True
        #     )

        #     # Add uploaders for each student
        #     for index, row in df.iterrows():
        #         uploaded_file = st.file_uploader(f"Upload Resume for {row['student_name']}", key=row['student_name'], label_visibility="collapsed")
        #         if uploaded_file is not None:
        #             # Save the uploaded file to the 'uploads' directory
        #             upload_dir = "uploads"
        #             os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
        #             save_path = os.path.join(upload_dir, uploaded_file.name)
        #             with open(save_path, "wb") as f:
        #                 f.write(uploaded_file.getbuffer())

        #             # Update the database with the new file information
        #             connection = sqlite3.connect(db_path)
        #             cursor = connection.cursor()
        #             cursor.execute('''
        #                 UPDATE uploads
        #                 SET file_name = ?, file_path = ?, uploaded_at = CURRENT_TIMESTAMP
        #                 WHERE student_name = ?
        #             ''', (uploaded_file.name, save_path, row['student_name']))
        #             connection.commit()
        #             connection.close()

        #             st.success(f"New resume for {row['student_name']} uploaded successfully!")
                # else:
                #     st.error("Please upload a file before clicking the upload button.")
    
    
    # else:
    #     st.write("No resumes found in the database.")

if __name__ == "__main__":
    main()
