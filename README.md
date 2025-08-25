# AI Agent Project

This project is an **AI-powered coding agent** designed to automatically debug and fix Python code within a specified codebase. It leverages **Google Gemini models** and a set of custom tools to analyze user prompts, inspect code files, identify bugs, apply fixes, and verify solutions.

---

## 🚀 Features
- Automated bug detection and fixing for Python projects  
- Uses **Google Gemini API** for intelligent code analysis  
- Modular tool system for file inspection, content retrieval, code execution, and file writing  
- Strict workflow to ensure only existing files are modified  
- Command-line interface with **verbose mode** for detailed output  

---

## 📦 Usage
Run the agent with a prompt describing your coding issue:

```bash
uv run main.py "Describe your bug or coding issue here" [--verbose]
```

# 📂 Project Structure

- **main.py** – Entry point and agent workflow  
- **functions/** – Modular tools for file operations and code execution  
- **calculator/** – Example submodule with sample code and tests  
- **.env** – Stores your `GEMINI_API_KEY` for API access  

---

# 🛠 Requirements

- Python **3.12+**  
- Google Gemini API key (set in `.env`)  
- Required packages listed in **pyproject.toml**  

---

# ⚙️ How It Works

1. Receives a user prompt describing a bug or coding task  
2. Inspects relevant files and code sections  
3. Identifies and applies code fixes  
4. Verifies the fix by running the affected code  
5. Provides a clear summary of the fix and verification result  
