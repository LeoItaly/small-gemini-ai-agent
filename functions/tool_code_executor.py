import os
import json # For pretty printing arguments in verbose mode
from google.genai import types

# Import the actual function implementations
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

def call_function(function_call_part, verbose=False):
    """
    Handles the abstract task of calling one of our four defined functions.
    It automatically injects the working_directory and formats the response
    for the LLM.

    Args:
        function_call_part (types.FunctionCall): The function call object
                                                 from the LLM's response.
        verbose (bool, optional): If True, prints detailed function call info.
                                  Defaults to False.

    Returns:
        types.Content: A Content object representing the result of the
                       function call, or an error.
    """
    # Hardcoded working directory for security.
    # This ensures the LLM cannot manipulate the base directory.
    working_directory = "./calculator"

    function_name = function_call_part.name
    
    # Convert args from MessageMap (immutable) to a mutable dictionary
    function_args = dict(function_call_part.args) 

    # Add the hardcoded working_directory to the arguments.
    # The LLM doesn't specify this for security reasons, so we inject it.
    function_args["working_directory"] = working_directory

    # --- CHANGE STARTS HERE ---
    if verbose:
        # Detailed output for verbose mode
        print(f"Calling function: {function_name}({json.dumps(function_args)})")
    else:
        # Minimal output for non-verbose mode, matching test expectations
        print(function_name) 
    # --- CHANGE ENDS HERE ---

    # Map function names (strings from LLM) to actual Python function objects
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    # Validate that the LLM requested a known function
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        # Call the actual Python function using dictionary unpacking (**)
        # This passes keyword arguments to the function.
        function_result = function_map[function_name](**function_args)
        
        # Return the result formatted as a tool response for the LLM
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result}, # Wrap string result in a dict
                )
            ],
        )
    except Exception as e:
        # If any error occurs during function execution, capture and return it
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error executing {function_name}: {e}"},
                )
            ],
        )
