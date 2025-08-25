import os
import subprocess
import sys
from google.genai import types

def run_python_file(working_directory, file_path, args=None):
    """
    Executes a Python file within a specified working directory, capturing its output.
    Includes security guardrails, a timeout, and robust error handling.

    Args:
        working_directory (str): The absolute or relative path to the base directory
                                 from which file operations are permitted.
        file_path (str): The relative path to the Python file to execute
                         within the working_directory.
        args (list, optional): A list of strings representing command-line arguments
                               to pass to the executed Python script. Defaults to [].

    Returns:
        str: A formatted string containing the script's stdout, stderr, and exit code,
             or an error message (prefixed with "Error:") if something went wrong.
             Returns "No output produced." if both stdout and stderr are empty.
    """
    if args is None:
        args = []

    try:
        # Resolve the absolute path of the working directory
        abs_working_directory = os.path.abspath(working_directory)
        
        # Construct the full path to the target file
        potential_full_path = os.path.join(abs_working_directory, file_path)
        full_path = os.path.normpath(potential_full_path)
        
        # Crucial Security Guardrail:
        # Ensure that the resolved full_path is a subdirectory of (or the same as)
        # the abs_working_directory. This prevents the agent from executing
        # files/directories outside its designated workspace.
        abs_full_path = os.path.abspath(full_path) # Get absolute path after normpath
        if not abs_full_path.startswith(abs_working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Validate that the target path is indeed an existing file
        if not os.path.isfile(abs_full_path):
            return f'Error: File "{file_path}" not found.'

        # Validate that the file ends with ".py"
        if not file_path.lower().endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # Construct the command to run the Python script
        # Using 'python3' for explicit Python 3 execution, common in WSL/Linux environments
        command = [sys.executable, abs_full_path] + list(args)

        # Execute the Python file using subprocess.run
        # - timeout: prevents infinite execution
        # - capture_output: captures stdout and stderr
        # - text=True: decodes stdout/stderr as text (UTF-8 by default)
        # - cwd: sets the current working directory for the subprocess
        process = subprocess.run(
            command,
            timeout=30,  # 30-second timeout
            capture_output=True,
            text=True,
            cwd=abs_working_directory,
            check=False # Do not raise CalledProcessError for non-zero exit codes, handle manually
        )

        output_lines = []
        if process.stdout:
            output_lines.append("STDOUT:")
            output_lines.append(process.stdout.strip())
        
        if process.stderr:
            output_lines.append("STDERR:")
            output_lines.append(process.stderr.strip())

        if process.returncode != 0:
            output_lines.append(f"Process exited with code {process.returncode}")

        if not output_lines:
            return "No output produced."
        
        return "\n".join(output_lines)

    except subprocess.TimeoutExpired:
        return f"Error: Execution of '{file_path}' timed out after 30 seconds."
    except FileNotFoundError:
        return f'Error: Python interpreter or file "{file_path}" not found.'
    except Exception as e:
        # Catch any other unexpected errors during setup or execution
        return f"Error: executing Python file: {e}"

# Function Declaration for the LLM to understand how to call run_python_file
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file within the working directory, capturing its standard output and error. "
                "The execution is limited to 30 seconds.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of string arguments to pass to the Python script.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)