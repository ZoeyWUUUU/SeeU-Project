# SeeU-project-Team3

1. Replace the OpenAI API key in `key.txt` with your own key. Alternatively, use Qwen model from Ali, and replace the Ali API key in `ali_key.txt` with your own key.
2. To run the code, 

    - By directly importing the function `read_resume` from `resume_interface.py`
        ```python
        from resume_interface import read_resume
        ```
        - `file_path`: The path of the resume file.
        - `file_object`: Alternative way to input the resume file.
        - `detailed_level`: `ExperienceType.SUMMARY` by default. *Final version TBD by Team 1.*
    - By running the script `resume_interface.py` directly
        ```python
        python resume_interface.py
        ```
        - `--file_path`: The path of the resume file.
        - `--detailed_level`: String type. See `-h` for more details.
        - `--output`: The path of the output file. Default `None` and print in terminal.
