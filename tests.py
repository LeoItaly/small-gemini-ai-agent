import os
import sys
import subprocess
from functions.run_python import run_python_file

# # --- Setup for specific calculator/main.py behavior for tests ---
# # This part ensures that 'calculator/main.py' behaves as expected for the tests.
# # If your 'calculator/main.py' already handles command-line arguments,
# # you might not strictly need to overwrite it, but this ensures consistency.
# def setup_calculator_main():
#     calculator_dir = "calculator"
#     os.makedirs(calculator_dir, exist_ok=True)
    
#     main_py_path = os.path.join(calculator_dir, "main.py")
#     # This content for main.py will print usage or a calculation result
#     main_py_content = """
# import sys

# def calculate(expression):
#     try:
#         # A simple eval for demonstration. In real apps, use a safer parser.
#         return str(eval(expression))
#     except Exception as e:
#         return f"Error: {e}"

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python main.py \"<expression>\"")
#     else:
#         expression = sys.argv[1]
#         print(f"Result: {calculate(expression)}")
# """
#     with open(main_py_path, "w", encoding="utf-8") as f:
#         f.write(main_py_content.strip())
#     print(f"Ensured '{main_py_path}' is set up for calculation tests.")

#     tests_py_path = os.path.join(calculator_dir, "tests.py")
#     tests_py_content = """
# # Dummy test file for execution demonstration
# print("Running dummy calculator tests...")
# print("Test 1: Passed")
# print("Test 2: Failed - some_condition not met")
# """
#     with open(tests_py_path, "w", encoding="utf-8") as f:
#         f.write(tests_py_content.strip())
#     print(f"Ensured '{tests_py_path}' is set up for execution tests.")


# --- Test function calls ---
def run_all_python_tests():
    print("Running run_python_file tests...\n")


    # Test 1: Run main.py without arguments (should show usage)
    print('Testing run_python_file("calculator", "main.py"):')
    result1 = run_python_file("calculator", "main.py")
    print("Result for 'main.py' (usage instructions):")
    print(result1)
    print("-" * 30)

    # Test 2: Run main.py with arguments (should run calculation)
    print('Testing run_python_file("calculator", "main.py", ["3 + 5"]):')
    result2 = run_python_file("calculator", "main.py", ["3 + 5"])
    print("Result for 'main.py' (calculation):")
    print(result2)
    print("-" * 30)
    
    # Test 3: Run tests.py
    print('Testing run_python_file("calculator", "tests.py"):')
    result3 = run_python_file("calculator", "tests.py")
    print("Result for 'tests.py':")
    print(result3)
    print("-" * 30)

    # Test 4: Attempt to run a file outside the working directory (should fail)
    # This assumes a 'main.py' might exist in the project root.
    # If not, the error might be "File not found" instead of "outside permitted directory".
    # For robust testing, we assume a 'main.py' might be outside 'calculator'.
    # We will create a dummy main.py in the root just for this test if it doesn't exist
    root_main_py_path = "main.py"
    if not os.path.exists(root_main_py_path):
        with open(root_main_py_path, "w") as f:
            f.write("print('Hello from root main.py')")
        print(f"Created dummy '{root_main_py_path}' for 'outside directory' test.")

    print('Testing run_python_file("calculator", "../main.py"):')
    result4 = run_python_file("calculator", "../main.py")
    print("Result for '../main.py' (expected error - outside directory):")
    print(result4)
    if os.path.exists(root_main_py_path):
        os.remove(root_main_py_path) # Clean up dummy root main.py
    print("-" * 30)


    # Test 5: Attempt to run a non-existent Python file (should fail)
    print('Testing run_python_file("calculator", "nonexistent.py"):')
    result5 = run_python_file("calculator", "nonexistent.py")
    print("Result for 'nonexistent.py' (expected error - file not found):")
    print(result5)
    print("-" * 30)
    

if __name__ == "__main__":
    run_all_python_tests()

