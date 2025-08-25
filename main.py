import os
import sys
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import all function schemas
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file import schema_write_file

# Import the call_function from our executor module
from functions.tool_code_executor import call_function


def main():
    verbose = False 

    if len(sys.argv) < 2:
        print("Error: Please provide a prompt as a command-line argument.")
        print("Usage: uv run main.py \"Your prompt here\" [--verbose]")
        sys.exit(1)

    user_prompt = sys.argv[1] 

    if len(sys.argv) > 2:
        if sys.argv[2] == "--verbose":
            verbose = True
        else:
            print(f"Error: Unknown argument '{sys.argv[2]}'. Did you mean --verbose?")
            print("Usage: uv run main.py \"Your prompt here\" [--verbose]")
            sys.exit(1)

    # --- STRICT SYSTEM PROMPT ---
    system_prompt = """
You are a helpful AI coding agent. Your ONLY goal is to debug and FIX Python code in the existing codebase, specifically in the working directory.

When a user reports a bug:
1. **Understand the problem**: Analyze the user's bug description and expected vs. actual output.
2. **Inspect files**: Use `get_files_info` to list files and `get_file_content` to read relevant code files (e.g., `calculator/pkg/calculator.py`).
3. **Identify the bug**: Pinpoint the exact location and cause of the error in the code.
4. **Apply the fix**: Use ONLY `write_file` to update the problematic file (e.g., `calculator/pkg/calculator.py`) with the corrected code. DO NOT create new files unless explicitly requested.
5. **Verify the fix**: Use `run_python_file` to execute the affected script (e.g., `calculator/main.py`) with the original problematic input to confirm the bug is resolved and the output matches the expected result.
6. **Final Answer**: Once the bug is confirmed to be fixed, provide a clear, concise explanation of what the bug was, how you fixed it, and the verification result.

You MUST update the actual code file containing the bug. Do NOT write a new file or script unless the user asks for it. All paths should be relative to the working directory (`./calculator`). The working directory is automatically injected for security reasons.
"""
    # --- END STRICT SYSTEM PROMPT ---

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file or environment variables.")
        sys.exit(1)

    model_name = "gemini-2.0-flash-001"
    client = genai.Client(api_key=api_key)

    print("Hello from ai-agent-project!")

    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"System instruction: {system_prompt}") 

    final_response_text = None
    verification_passed = False
    max_iterations = 20


    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Agent Turn {i+1}/{max_iterations} ---")

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt,
                    max_output_tokens=2048
                )
            )

            # Track if agent claims problem is solved
            agent_claims_solved = False
            verification_step_present = False

            if response.candidates:
                for candidate in response.candidates:
                    messages.append(candidate.content)

                    has_text_response = False
                    if candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                final_response_text = part.text
                                has_text_response = True
                                # Check for keywords indicating the agent claims the problem is solved
                                solved_keywords = ["fixed", "resolved", "success", "solved", "completed", "corrected"]
                                if any(kw in part.text.lower() for kw in solved_keywords):
                                    agent_claims_solved = True
                                break
                    if has_text_response:
                        break

            if response.function_calls:
                for function_call_part in response.function_calls:
                    if verbose:
                        print(f"Calling function: {function_call_part.name}({json.dumps(dict(function_call_part.args))})")
                    else:
                        print(f"{function_call_part.name}")

                    function_call_result_content = call_function(function_call_part)

                    if not (function_call_result_content.parts and
                            len(function_call_result_content.parts) > 0 and
                            function_call_result_content.parts[0].function_response and
                            function_call_result_content.parts[0].function_response.response is not None):
                        raise ValueError("Unexpected structure in function_call_result from call_function.")

                    actual_response_data = function_call_result_content.parts[0].function_response.response

                    # Mark that a verification step was present if run_python_file was called
                    if function_call_part.name == "run_python_file":
                        verification_step_present = True

                    if verbose:
                        if "result" in actual_response_data:
                            print(f"-> {actual_response_data['result']}")
                        elif "error" in actual_response_data:
                            print(f"-> ERROR: {actual_response_data['error']}")
                        else:
                            print(f"-> Raw function response: {actual_response_data}")

                    messages.append(function_call_result_content)
            else:
                if verbose:
                    print("Model returned no text and no function calls. Ending loop.")
                break

            # Only exit if agent claims problem is solved AND a verification step was present
            if agent_claims_solved and verification_step_present:
                break

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")
            sys.exit(1)

    print("\nFinal response:")
    if final_response_text:
        print(final_response_text)
    else:
        print("Agent did not produce a final text response within the iteration limit, or encountered an issue.")
        if verbose:
            print("Last few messages in conversation:")
            for msg in messages[-5:]:
                print(msg)

    if verbose and 'response' in locals() and response.usage_metadata:
        print(f"\nPrompt tokens (last turn): {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens (last turn): {response.usage_metadata.candidates_token_count}")
    elif verbose:
        print("\nUsage metadata not available for the final turn.")


if __name__ == "__main__":
    main()
