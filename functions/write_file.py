import os
from google.genai import types 

def write_file(working_directory, file_path, content):
    """
    Writes or overwrites content to a file within a specified working directory.
    Includes security guardrails to prevent access outside the working_directory,
    creates parent directories if necessary, and provides clear feedback.

    Args:
        working_directory (str): The absolute or relative path to the base directory
                                 from which file operations are permitted.
        file_path (str): The relative path to the target file
                         within the working_directory.
        content (str): The string content to write to the file.

    Returns:
        str: A success message if the write operation is successful,
             or an error message (prefixed with "Error:") if something went wrong.
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
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Ensure the directory for the file exists
        target_directory = os.path.dirname(abs_full_path)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory, exist_ok=True) # Create all necessary parent directories

        # Write the content to the file, overwriting existing content
        with open(abs_full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except OSError as e:
        # Catch OS-related errors (e.g., permission denied, disk full)
        return f"Error: An OS error occurred while writing to \"{file_path}\": {e}"
    except Exception as e:
        # Catch any other unexpected errors
        return f"Error: An unexpected error occurred while writing to \"{file_path}\": {e}"

# Function Declaration for the LLM to understand how to call write_file
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a file within the working directory. "
                "Creates the file and any necessary parent directories if they do not exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The string content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)