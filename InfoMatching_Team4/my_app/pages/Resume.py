# pages/1_Resume.py

import streamlit as st
import sqlite3
import os
import pandas as pd

def main():
    st.title("Resume Page")

    # Add a text input for the new student name
    new_student_name = st.text_input("Enter Student Name")
    new_uploaded_resume = st.file_uploader("Upload Resume for Student")

    if new_student_name and new_uploaded_resume:
        # Save the uploaded file to the 'uploads' directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
        save_path = os.path.join(upload_dir, new_uploaded_resume.name)
        with open(save_path, "wb") as f:
            f.write(new_uploaded_resume.getbuffer())

        # Check if the student name already exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "../../", "my_database.db")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM uploads WHERE student_name = ?", (new_student_name,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Update the existing entry
            cursor.execute('''
                UPDATE uploads
                SET file_name = ?, file_path = ?, uploaded_at = CURRENT_TIMESTAMP
                WHERE student_name = ?
            ''', (new_uploaded_resume.name, save_path, new_student_name))
        else:
            # Insert a new entry
            cursor.execute('''
                INSERT INTO uploads (student_name, file_name, file_path)
                VALUES (?, ?, ?)
            ''', (new_student_name, new_uploaded_resume.name, save_path))

        connection.commit()
        connection.close()

        st.success(f"New resume for {new_student_name} uploaded successfully!")


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
        
        # Convert file_path to clickable links
        server_url = "http://localhost:8000"
        df['file_path'] = df['file_path'].apply(lambda x: f'<a href="{server_url}/{os.path.basename(x)}" download>{os.path.basename(x)}</a>')
        
        # Display the DataFrame with clickable links
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
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
    
    
    else:
        st.write("No resumes found in the database.")

if __name__ == "__main__":
    main()
