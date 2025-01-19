# pages/2_Job_Description.py

import streamlit as st
import sqlite3
import os
import pandas as pd

def main():
    st.title("Job Description Page")

    # Add a file uploader for the job description Excel file
    uploaded_file = st.file_uploader("Upload Job Description Excel File", type=["xlsx"])

    if uploaded_file is not None:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)

        # Insert the data into the job_description table
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "../../", "my_database.db")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Iterate over the DataFrame and insert each row into the database
        for index, row in df.iterrows():
            # Check if the entry already exists in the database
            cursor.execute('''
                SELECT COUNT(*) FROM job_description
                WHERE job_company = ? AND job_title = ? AND job_description = ? AND job_application_url = ?
            ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the row if it does not exist
                cursor.execute('''
                    INSERT INTO job_description (job_company, job_title, job_description, job_application_url)
                    VALUES (?, ?, ?, ?)
                ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))
        
        connection.commit()
        connection.close()

        st.success("Job descriptions uploaded successfully!")

    # # Add text inputs for search criteria
    # company_name = st.text_input("Enter Company Name to Filter Results")
    # job_title = st.text_input("Enter Job Title to Filter Results")
    # job_description = st.text_input("Enter Job Description to Filter Results")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../../", "my_database.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM job_description")
    
    # Build the query based on search criteria
    # query = "SELECT * FROM job_description WHERE 1=1"
    # params = []

    # if company_name:
    #     query += " AND job_company LIKE ?"
    #     params.append(f"%{company_name}%")

    # if job_title:
    #     query += " AND job_title LIKE ?"
    #     params.append(f"%{job_title}%")

    # if job_description:
    #     query += " AND job_description LIKE ?"
    #     params.append(f"%{job_description}%")

    # cursor.execute(query, params)
    
    data = cursor.fetchall()

    # Fetch column names
    cursor.execute("PRAGMA table_info(job_description)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]

    connection.close()

    if data:
        st.subheader("Job Description Table Data")
        df = pd.DataFrame(data, columns=column_names)

        # # Initialize session state for filtered DataFrame
        # if 'filtered_df' not in st.session_state:
        #     st.session_state.filtered_df = df

        # # Print the type of data in the created_at column
        # print("Data type of 'created_at' column:", df['created_at'].dtype)

        # st.table(data)
        # st.table(df)
        # Exclude job_application_url from filter options
        # filter_columns = [col for col in column_names if col != 'job_application_url']
        filter_columns = [col for col in column_names]
        
        # Add a multiselect widget for filtering the DataFrame columns
        selected_columns = st.multiselect("Filter columns", options=filter_columns, default=filter_columns)
        filtered_df = df[selected_columns]

        # filtered_df = st.session_state.filtered_df[selected_columns]

        # # Debug: Print the columns of filtered_df
        # st.write("Columns in filtered_df:", filtered_df.columns)

        # if 'created_at' in filtered_df.columns:
        #     min_date = filtered_df['created_at'].min()
        #     max_date = filtered_df['created_at'].max()
        #     selected_date = st.slider(f"Filter created_at", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD", key='created_at')
        #     if selected_date:
        #         filtered_df = filtered_df[(filtered_df['created_at'] >= selected_date[0]) & (filtered_df['created_at'] <= selected_date[1])]
        # else:
        #     st.error("Column 'created_at' not found in the DataFrame.")
        
        # # Add filters for each selected column except job_application_url
        # for column in selected_columns:
        #     if column != 'job_description':  # Skip job_description as it has its own text input
        #         unique_values = filtered_df[column].unique()
        #         selected_values = st.multiselect(f"Filter values for {column}", options=unique_values, default=unique_values)
        #         filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
        
        # Add filters for each selected column except job_application_url
        for column in selected_columns:
            if column == 'created_at':
                # # Fill NaT values with a default date
                # filtered_df[column] = pd.to_datetime(filtered_df[column]).fillna(pd.Timestamp("1970-01-01"))
                min_date = pd.to_datetime(filtered_df[column]).min().date()
                max_date = pd.to_datetime(filtered_df[column]).max().date()
                if min_date == max_date:
                    st.write(f"No date range available for {column}.")
                else:
                    selected_date = st.slider(f"Filter {column}", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD", key=column)
                    if selected_date:
                        filtered_df = filtered_df[(pd.to_datetime(filtered_df[column]).dt.date >= selected_date[0]) & (pd.to_datetime(filtered_df[column]).dt.date <= selected_date[1])]
            if column in ['job_title', 'job_company', 'id']:
                unique_values = filtered_df[column].unique()
                selected_values = st.multiselect(f"Filter values for {column}", options=unique_values)
                if selected_values:
                    filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
            if column == 'job_description':
                filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
                if filter_input:
                    filtered_df = filtered_df[filtered_df[column].str.contains(filter_input, case=False)]
                    if filtered_df.empty:
                        break  # Exit the loop if no results match the input

        if filtered_df.empty:
            st.write("No result")
        else:
            st.dataframe(filtered_df)

        # # Update the multi-selection choices based on the filtered DataFrame
        # for column in selected_columns:
        #     if column != 'job_description' and column != 'job_application_url' and column != 'created_at':
        #         unique_values = filtered_df[column].unique()
        #         st.multiselect(f"Filter values for {column}", options=unique_values, key=f"updated_{column}")


    else:
        st.write("No job descriptions found.")

if __name__ == "__main__":
    main()

