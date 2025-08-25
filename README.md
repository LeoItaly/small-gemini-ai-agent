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
