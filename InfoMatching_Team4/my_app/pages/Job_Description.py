# pages/2_Job_Description.py

import streamlit as st
import sqlite3
import os
import pandas as pd
import sys
import re

# Append the path to the parent directory of InfoMatching_Team2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../InfoMatching_Team2')))
from jd_function import extract_job_data, client

def sanitize_column_name(name):
    # Replace spaces and special characters with underscores
    return re.sub(r'\W|^(?=\d)', '_', name)

def main():
    
    # Create columns for the title and file uploader
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Job Description")
    # with col2:
    #     # Add a file uploader for the job description Excel file
    #     uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    # Move the file uploader to the sidebar
    with st.sidebar:
        # st.header("Upload Job Description")
        # Add a file uploader for the job description Excel file
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file is not None:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)

        # Insert the data into the job_description table
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "../../", "my_database.db")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Get existing columns in the job_description table
        cursor.execute("PRAGMA table_info(job_description)")
        existing_columns = [info[1] for info in cursor.fetchall()]

        # Iterate over the DataFrame and insert each row into the database
        for index, row in df.iterrows():

            # Extract job data using the extract_job_data function
            extracted_data = extract_job_data(row['job_description'])

            # print(extracted_data)

            # Add new columns to the job_description table based on the JSON keys
            for key in extracted_data.keys():
                sanitized_key = sanitize_column_name(key)
                # if key not in existing_columns:
                if sanitized_key not in existing_columns:
                    cursor.execute(f"ALTER TABLE job_description ADD COLUMN {sanitized_key} TEXT")
                    existing_columns.append(sanitized_key)
                # cursor.execute(f"ALTER TABLE job_description ADD COLUMN IF NOT EXISTS {key} TEXT")
                # print(existing_columns)

            # Prepare the data for insertion
            data = {
                'job_company': row['job_company'],
                'job_title': row['job_title'],
                'job_description': row['job_description'],
                'job_application_url': row['job_application_url'],
                # **extracted_data
                # **{sanitize_column_name(k): (v if v else None) for k, v in extracted_data.items()}
                **{sanitize_column_name(k): (', '.join(v) if isinstance(v, list) else v) for k, v in extracted_data.items()}
            }

            # Check if the entry already exists in the database
            cursor.execute('''
                SELECT COUNT(*) FROM job_description
                WHERE job_company = ? AND job_title = ? AND job_description = ? AND job_application_url = ?
            ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the row if it does not exist
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                cursor.execute(f'''
                    INSERT INTO job_description ({columns})
                    VALUES ({placeholders})
                ''', list(data.values()))

            # # Parse the resultant JSON info
            # company_industry_field = extracted_data.get('Company Industry Field', '')
            # major = extracted_data.get('Major', '')
            # tech_skills = extracted_data.get('Tech skills', '')
            # graduation_time = extracted_data.get('graduation time', '')
            # qualification = extracted_data.get('minimum academic qualification and Experience domain', '')

            #  # Convert lists to strings if necessary
            # if(isinstance(company_industry_field, list)):
            #     company_industry_field = ', '.join(company_industry_field)
            # if isinstance(major, list):
            #     major = ', '.join(major)
            # if isinstance(tech_skills, list):
            #     tech_skills = ', '.join(tech_skills)
            # if isinstance(graduation_time, list):
            #     graduation_time = ', '.join(graduation_time)
            # if isinstance(qualification, list):
            #     qualification = ', '.join(qualification)

            # # Check if the entry already exists in the database
            # cursor.execute('''
            #     SELECT COUNT(*) FROM job_description
            #     WHERE job_company = ? AND job_title = ? AND job_description = ? AND job_application_url = ?
            # ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))
            # count = cursor.fetchone()[0]

            # if count == 0:
            #     # # Insert the row if it does not exist
            #     # cursor.execute('''
            #     #     INSERT INTO job_description (job_company, job_title, job_description, job_application_url)
            #     #     VALUES (?, ?, ?, ?)
            #     # ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url']))
            #     # Insert the row if it does not exist
            #     cursor.execute('''
            #         INSERT INTO job_description (job_company, job_title, job_description, job_application_url, company_industry_field, major, tech_skills, graduation_time, qualification)
            #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            #     ''', (row['job_company'], row['job_title'], row['job_description'], row['job_application_url'], company_industry_field, major, tech_skills, graduation_time, qualification))
        
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
        # st.subheader("Job Description Table Data")
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
        # Add a multiselect widget for filtering the DataFrame columns in the sidebar
        with st.sidebar:
            # st.header("Filters")
        
            filter_columns = [col for col in column_names]
            
            # Add a multiselect widget for filtering the DataFrame columns
            # st.write("Select columns to filter:")
            # selected_columns = st.multiselect("Filter columns", options=filter_columns, default=filter_columns)
            # filtered_df = df[selected_columns]
            # Add a multiselect widget for selecting columns to display
            # st.write("Select columns to display:")
            selected_columns = st.multiselect("Display columns", options=filter_columns, default=filter_columns)
            # displayed_df = df[selected_columns]

            # st.write("Apply filters to columns:")
            # st.write("NOTE: please fill out filters in top-down order")

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

            # Add filters for each column

            # Initialize query parts
            query = "SELECT * FROM job_description WHERE 1=1"
            params = []

            # # Group filters into "Basics" and "Specific"
            # with st.expander("Basics"):
            #     for column in ['job_title', 'job_company', 'id']:
            #         if column not in st.session_state:
            #             st.session_state[column] = []
            #         selected_values = st.multiselect(f"Filter values for {column}", options=df[column].unique(), key=column)
            #         st.session_state[column] = selected_values
            #         if selected_values:
            #             query += f" AND ({column} IN ({','.join(['?']*len(selected_values))}) OR {column} IS NULL)"
            #             params.extend(selected_values)

            # with st.expander("Specific"):
            #     for column in ['job_description', 'company_industry_field', 'major', 'tech_skills', 'qualification']:
            #         if column not in st.session_state:
            #             st.session_state[column] = ""
            #         filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
            #         st.session_state[column] = filter_input
            #         if filter_input:
            #             query += f" AND ({column} LIKE ? OR {column} IS NULL)"
            #             params.append(f"%{filter_input}%")
            #     if 'graduation_time' not in st.session_state:
            #         st.session_state['graduation_time'] = ""
            #     filter_input = st.text_input(f"Filter graduation_time (case insensitive)", key='graduation_time')
            #     st.session_state['graduation_time'] = filter_input
            #     if filter_input:
            #         query += f" AND (graduation_time LIKE ? OR graduation_time IS NULL OR graduation_time = 'not specified')"
            #         params.append(f"%{filter_input}%")

            # Add filters for each column WITH SESSION STATE
            for column in filter_columns:
                if column not in st.session_state:
                    st.session_state[column] = ""
                filter_input = st.text_input(f"Filter {column} (case insensitive)", value=st.session_state[column], key=column)
                # st.session_state[column] = filter_input
                if filter_input:
                    query += f" AND ({column} LIKE ? OR {column} IS NULL)"
                    params.append(f"%{filter_input}%")
                # # if column == 'created_at':
                # #     if f"{column}_min" not in st.session_state:
                # #         st.session_state[f"{column}_min"] = pd.to_datetime(df[column]).min().date()
                # #     if f"{column}_max" not in st.session_state:
                # #         st.session_state[f"{column}_max"] = pd.to_datetime(df[column]).max().date()
                # #     selected_date = st.slider(f"Filter {column}", min_value=st.session_state[f"{column}_min"], max_value=st.session_state[f"{column}_max"], value=(st.session_state[f"{column}_min"], st.session_state[f"{column}_max"]), format="YYYY-MM-DD", key=column)
                # #     if selected_date:
                # #         query += " AND (created_at BETWEEN ? AND ? OR created_at IS NULL)"
                # #         params.extend([selected_date[0], selected_date[1]])
                # if column in ['job_title', 'job_company', 'id']:
                #     if column not in st.session_state:
                #         st.session_state[column] = []
                #     # selected_values = st.multiselect(f"Filter values for {column}", options=df[column].unique(), default=st.session_state[column], key=column)
                #     selected_values = st.multiselect(f"Filter values for {column}", options=df[column].unique(), key=column)

                #     if selected_values:
                #         query += f" AND ({column} IN ({','.join(['?']*len(selected_values))}) OR {column} IS NULL)"
                #         params.extend(selected_values)
                # elif column in ['job_description', 'company_industry_field', 'major', 'tech_skills', 'qualification']:
                #     if column not in st.session_state:
                #         st.session_state[column] = ""
                #     filter_input = st.text_input(f"Filter {column} (case insensitive)", value=st.session_state[column], key=column)
                #     if filter_input:
                #         query += f" AND ({column} LIKE ? OR {column} IS NULL)"
                #         params.append(f"%{filter_input}%")
                # elif column == 'graduation_time':
                #     if column not in st.session_state:
                #         st.session_state[column] = ""
                #     filter_input = st.text_input(f"Filter {column} (case insensitive)", value=st.session_state[column], key=column)
                #     if filter_input:
                #         query += f" AND ({column} LIKE ? OR {column} IS NULL OR {column} = 'not specified')"
                #         params.append(f"%{filter_input}%")

            # # Add filters for each column WITHOUT SESSION STATE
            # for column in filter_columns:
            #     if column == 'created_at':
            #         min_date = pd.to_datetime(df[column]).min().date()
            #         max_date = pd.to_datetime(df[column]).max().date()
            #         if min_date != max_date:
            #             selected_date = st.slider(f"Filter {column}", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD", key=column)
            #             if selected_date:
            #                 query += " AND (created_at BETWEEN ? AND ? OR created_at IS NULL)"
            #                 params.extend([selected_date[0], selected_date[1]])
            #     elif column in ['job_title', 'job_company', 'id']:
            #         unique_values = df[column].unique()
            #         selected_values = st.multiselect(f"Filter values for {column}", options=unique_values)
            #         if selected_values:
            #             query += f" AND ({column} IN ({','.join(['?']*len(selected_values))}) OR {column} IS NULL)"
            #             params.extend(selected_values)
            #     elif column in ['job_description', 'company_industry_field', 'major', 'tech_skills', 'qualification']:
            #         filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
            #         if filter_input:
            #             query += f" AND ({column} LIKE ? OR {column} IS NULL)"
            #             params.append(f"%{filter_input}%")
            #     elif column == 'graduation_time':
            #         filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
            #         if filter_input:
            #             query += f" AND ({column} LIKE ? OR {column} IS NULL OR {column} = 'not specified')"
            #             params.append(f"%{filter_input}%")

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
                

        # Display the filtered DataFrame based on selected columns
        if apply_filter:
            # Execute the query with the filters
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(query, params)
            filtered_data = cursor.fetchall()
            connection.close()

            # Convert the filtered data to a DataFrame
            filtered_df = pd.DataFrame(filtered_data, columns=column_names)

            if filtered_df.empty:
                st.write("No result")
            else:
                st.dataframe(filtered_df[selected_columns])
        elif clear_filter:
            # Clear the filters by resetting the session state
            for column in filter_columns:
                if column in st.session_state:
                    del st.session_state[column]
                # if f"{column}_min" in st.session_state:
                #     del st.session_state[f"{column}_min"]
                # if f"{column}_max" in st.session_state:
                #     del st.session_state[f"{column}_max"]

            # Display the full DataFrame based on selected columns
            st.dataframe(df[selected_columns])
        else:
            # Display the full DataFrame based on selected columns if no filter is applied
            st.dataframe(df[selected_columns])




        #     for column in filter_columns:
        #         if column == 'created_at':
        #             min_date = pd.to_datetime(df[column]).min().date()
        #             max_date = pd.to_datetime(df[column]).max().date()
        #             if min_date == max_date:
        #                 st.write(f"No date range available for {column}.")
        #             else:
        #                 selected_date = st.slider(f"Filter {column}", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD", key=column)
        #                 if selected_date:
        #                     df = df[(pd.to_datetime(df[column]).dt.date >= selected_date[0]) & (pd.to_datetime(df[column]).dt.date <= selected_date[1])]
        #         elif column in ['job_title', 'job_company', 'id']:
        #             unique_values = df[column].unique()
        #             selected_values = st.multiselect(f"Filter values for {column}", options=unique_values)
        #             if selected_values:
        #                 df = df[df[column].isin(selected_values)]
        #         elif column in ['job_description', 'company_industry_field', 'major', 'tech_skills', 'graduation_time', 'qualification']:
        #             filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
        #             if filter_input:
        #                 df = df[df[column].str.contains(filter_input, case=False)]
        #                 if df.empty:
        #                     break  # Exit the loop if no results match the input

        # if df.empty:
        #     st.write("No result")
        # else:
        #     st.dataframe(displayed_df)

        #     for column in selected_columns:
        #         if column == 'created_at':
        #             # # Fill NaT values with a default date
        #             # filtered_df[column] = pd.to_datetime(filtered_df[column]).fillna(pd.Timestamp("1970-01-01"))
        #             min_date = pd.to_datetime(filtered_df[column]).min().date()
        #             max_date = pd.to_datetime(filtered_df[column]).max().date()
        #             if min_date == max_date:
        #                 st.write(f"No date range available for {column}.")
        #             else:
        #                 selected_date = st.slider(f"Filter {column}", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD", key=column)
        #                 if selected_date:
        #                     filtered_df = filtered_df[(pd.to_datetime(filtered_df[column]).dt.date >= selected_date[0]) & (pd.to_datetime(filtered_df[column]).dt.date <= selected_date[1])]
        #         if column in ['job_title', 'job_company', 'id']:
        #             unique_values = filtered_df[column].unique()
        #             selected_values = st.multiselect(f"Filter values for {column}", options=unique_values)
        #             if selected_values:
        #                 filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
        #         if column in ['job_description', 'company_industry_field', 'major', 'tech_skills', 'graduation_time', 'qualification']:
        #             filter_input = st.text_input(f"Filter {column} (case insensitive)", key=column)
        #             if filter_input:
        #                 filtered_df = filtered_df[filtered_df[column].str.contains(filter_input, case=False)]
        #                 if filtered_df.empty:
        #                     break  # Exit the loop if no results match the input

        # if filtered_df.empty:
        #     st.write("No result")
        # else:
        #     # st.dataframe(filtered_df)
        #     st.dataframe(displayed_df)

        # # Update the multi-selection choices based on the filtered DataFrame
        # for column in selected_columns:
        #     if column != 'job_description' and column != 'job_application_url' and column != 'created_at':
        #         unique_values = filtered_df[column].unique()
        #         st.multiselect(f"Filter values for {column}", options=unique_values, key=f"updated_{column}")


    else:
        st.write("No job descriptions found.")

if __name__ == "__main__":
    main()

