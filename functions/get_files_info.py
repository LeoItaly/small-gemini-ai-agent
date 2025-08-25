import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    """
    Lists the contents of a directory within a specified working directory,
    including file names, sizes, and whether they are directories.
    Includes security guardrails to prevent access outside the working_directory.

    Args:
        working_directory (str): The absolute or relative path to the base directory
                                 from which operations are permitted.
        directory (str, optional): The relative path to the target directory
                                   within the working_directory. Defaults to ".".

    Returns:
        str: A formatted string representing the directory contents, or an error message.
             Format: "- filename: file_size=X bytes, is_dir=True/False"
             Error strings are prefixed with "Error:".
    """
    try:
        # Resolve the absolute path of the working directory
        abs_working_directory = os.path.abspath(working_directory)
        
        # Construct the full path to the target directory
        # os.path.join safely combines paths, and os.path.normpath normalizes it
        # (e.g., resolves "a/b/../c" to "a/c")
        potential_full_path = os.path.join(abs_working_directory, directory)
        full_path = os.path.normpath(potential_full_path)
        
        # Crucial Security Guardrail:
        # Ensure that the resolved full_path is a subdirectory of (or the same as)
        # the abs_working_directory. This prevents the agent from accessing
        # files/directories outside its designated workspace.
        abs_full_path = os.path.abspath(full_path) # Get absolute path after normpath
        if not abs_full_path.startswith(abs_working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Validate that the target path is indeed a directory
        if not os.path.isdir(abs_full_path):
            return f'Error: "{directory}" is not a directory'

        # List the contents of the directory
        contents = os.listdir(abs_full_path)
        
        output_lines = []
        # Sort the contents for consistent output order
        for item_name in sorted(contents):
            item_path = os.path.join(abs_full_path, item_name)
            
            is_dir = os.path.isdir(item_path)
            
            file_size = 0
            try:
                # os.path.getsize returns the size for both files and directories (on some systems)
                file_size = os.path.getsize(item_path)
            except OSError:
                # If there's an error getting the size (e.g., permissions), default to 0
                file_size = 0

            output_lines.append(
                f"- {item_name}: file_size={file_size} bytes, is_dir={is_dir}"
            )
        
        # Join all the formatted lines into a single string
        return "\n".join(output_lines)
    
    except OSError as e:
        # Catch OS-related errors (e.g., file not found, permission denied)
        return f"Error: An OS error occurred: {e}"
    except Exception as e:
        # Catch any other unexpected errors
        return f"Error: An unexpected error occurred: {e}"

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
        # 'directory' is optional, so it's not in required list
        required=[] 
    ),
)