import os
from config import MAX_FILE_CHARS # Import the MAX_FILE_CHARS from your config.py
from google.genai import types

def get_file_content(working_directory, file_path):
    """
    Reads the content of a file within a specified working directory.
    Includes security guardrails, truncation, and error handling.

    Args:
        working_directory (str): The absolute or relative path to the base directory
                                 from which file operations are permitted.
        file_path (str): The relative path to the target file
                         within the working_directory.

    Returns:
        str: The content of the file (potentially truncated), or an error message.
             Error strings are prefixed with "Error:".
    """
    try:
        # Resolve the absolute path of the working directory
        abs_working_directory = os.path.abspath(working_directory)
        
        # Construct the full path to the target file
        potential_full_path = os.path.join(abs_working_directory, file_path)
        full_path = os.path.normpath(potential_full_path)
        
        # Crucial Security Guardrail:
        # Ensure that the resolved full_path is a subdirectory of (or the same as)
        # the abs_working_directory. This prevents the agent from accessing
        # files/directories outside its designated workspace.
        abs_full_path = os.path.abspath(full_path) # Get absolute path after normpath
        if not abs_full_path.startswith(abs_working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Validate that the target path is indeed a file, not a directory
        if not os.path.isfile(abs_full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Read the file content
        with open(abs_full_path, "r", encoding="utf-8") as f:
            file_content_string = f.read(MAX_FILE_CHARS + 1) # Read one more char to check if truncation is needed

        # Truncate if necessary and append a message
        if len(file_content_string) > MAX_FILE_CHARS:
            file_content_string = file_content_string[:MAX_FILE_CHARS]
            file_content_string += f'[...File "{file_path}" truncated at {MAX_FILE_CHARS} characters]'

        return file_content_string
    
    except FileNotFoundError:
        return f'Error: File not found: "{file_path}"'
    except IsADirectoryError:
        return f'Error: File not found or is not a regular file: "{file_path}"'
    except PermissionError:
        return f'Error: Permission denied to read file: "{file_path}"'
    except Exception as e:
        # Catch any other unexpected errors
        return f"Error: An unexpected error occurred while reading \"{file_path}\": {e}"

# Function Declaration for the LLM to understand how to call get_file_content
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specified file, constrained to the working directory. "
                "Truncates files longer than 10,000 characters and appends a truncation message.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)
