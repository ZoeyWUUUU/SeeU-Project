import streamlit as st
import pandas as pd
from io import StringIO
import os
import sqlite3

st.set_page_config(
    page_title="Upload Files",
    page_icon="Upload Files",
)

st.write("# Please Upload Resume or Job Description")

# Add a text input for the student name
student_name = st.text_input("Enter Student Name")

uploaded_resume = st.file_uploader("Upload Resume")
if uploaded_resume is not None:

    # bytes_data = uploaded_resume.getvalue()
    # st.write(bytes_data)

    # stringio = StringIO(uploaded_resume.getvalue().decode("utf-8"))
    # st.write(stringio)

    # string_data = stringio.read()
    # st.write(string_data)

    # dataframe = pd.read_csv(uploaded_resume)
    # st.write(dataframe)

    # Save the uploaded file to the 'uploads' directory
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
    save_path = os.path.join(upload_dir, uploaded_resume.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_resume.getbuffer())

    # Check if the file already exists in the database
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    # cursor.execute('SELECT COUNT(*) FROM uploads WHERE file_name = ?', (uploaded_resume.name,))
    cursor.execute('SELECT COUNT(*) FROM uploads WHERE student_name = ?', (student_name,))
    count = cursor.fetchone()[0]

    if count > 0:
        # Update the existing entry
        cursor.execute('''
            UPDATE uploads
            SET file_name = ?, file_path = ?, uploaded_at = CURRENT_TIMESTAMP
            WHERE student_name = ?
        ''', (uploaded_resume.name, save_path, student_name))
        # cursor.execute('''
        #     UPDATE uploads
        #     SET file_path = ?, uploaded_at = CURRENT_TIMESTAMP
        #     WHERE file_name = ?
        # ''', (save_path, uploaded_resume.name))
    else:
        # Insert a new entry
        cursor.execute('''
            INSERT INTO uploads (student_name, file_name, file_path)
            VALUES (?, ?, ?)
        ''', (student_name, uploaded_resume.name, save_path))

    connection.commit()
    connection.close()

#     # Insert file info into the database
#     connection = sqlite3.connect('my_database.db')
#     cursor = connection.cursor()

# #     cursor.execute('''
# #     INSERT INTO uploads (file_name, file_path)
# #     VALUES (?, ?)
# #     ON CONFLICT (id) DO UPDATE SET  
# #         file_name = excluded.file_name,
# #         file_path = excluded.file_path,
# #         uploaded_at = CURRENT_TIMESTAMP
# # ''', (uploaded_resume.name, save_path))

#     cursor.execute('''
#         INSERT INTO uploads (file_name, file_path)
#         VALUES (?, ?)
#     ''', (uploaded_resume.name, save_path))

#     connection.commit()
#     connection.close()

    st.success(f"File saved to {save_path} and information saved to the database.")

    # # Call the function with the file path
    # file_content = process_file(save_path)
    # st.write(file_content)

# st.button("Submit Resume")

# txt = st.text_area(
#     "Paste your job descroption below"
# )
# st.button("Submit Job Description")

uploaded_jd = st.file_uploader("Upload Job Description (Excel)", type=["xlsx"])
if uploaded_jd is not None:

    # Read the Excel file
    df = pd.read_excel(uploaded_jd)

    # Insert data into the job_description table
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO job_description (job_company, job_title, job_description, job_application_url)
            VALUES (?, ?, ?, ?)
        ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))

    connection.commit()

    # Calculate matching scores and insert into job_matching_result table
    cursor.execute("SELECT id FROM job_description")
    job_ids = cursor.fetchall()
    cursor.execute("SELECT id FROM uploads ORDER BY uploaded_at DESC LIMIT 1")
    last_resume_id = cursor.fetchone()[0]
    cursor.execute("SELECT student_name FROM uploads ORDER BY uploaded_at DESC LIMIT 1")
    last_student_name = cursor.fetchone()[0]

    for job_id in job_ids:
        # Example matching score calculation (replace with actual logic)
        matching_score = 0.8  # Placeholder score
        cursor.execute('''
            INSERT INTO job_matching_result (job_id, resume_id, student_name, matching_score)
            VALUES (?, ?, ?, ?)
        ''', (job_id[0], last_resume_id, last_student_name, matching_score))
        # cursor.execute('''
        #     INSERT INTO job_matching_result (job_id, resume_id, matching_score)
        #     VALUES (?, ?, ?)
        # ''', (job_id[0], last_resume_id, matching_score))
        # cursor.execute('''
        #     INSERT INTO job_matching_result (job_id, matching_score)
        #     VALUES (?, ?)
        # ''', (job_id[0], matching_score))

        # # Calculate matching score for each job_id
        # resume_text = open(save_path, 'r').read()  # Read the uploaded resume text
        # job_description_text = row['job_description']  # Get the job description text

        # # Example matching score calculation (replace with actual logic)
        # matching_score = calculate_matching_score(resume_text, job_description_text)

        # cursor.execute('''
        #     INSERT INTO job_matching_result (job_id, matching_score)
        #     VALUES (?, ?)
        # ''', (job_id[0], matching_score))

    connection.commit()
    connection.close()

    st.success("Job description information saved to the database.")