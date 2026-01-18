📋 Project Description

AI Code Reviewer is an intelligent documentation analysis and generation tool that leverages Large Language Models (LLMs) to automatically analyze Python codebases, identify missing or incomplete docstrings, and generate high-quality documentation in multiple standard formats.

The tool provides an interactive web interface for reviewing, comparing, and applying AI-generated docstrings directly to source code files. This project demonstrates the practical application of LLM-based text generation for software engineering, specifically addressing the challenge of maintaining comprehensive code documentation across large Python projects.

✨ Features
Core Capabilities

Automated Code Scanning
Recursively analyzes Python projects to extract functions, methods, and classes.

Multi-Style Docstring Generation
Generates docstrings in three widely used formats:

Google Style

NumPy Style

reStructuredText (reST) Style

Interactive Review Workflow
Side-by-side comparison of existing and AI-generated docstrings.

Direct File Modification
Automatically applies accepted docstrings to source files with proper indentation.

PEP 257 Validation
Checks docstring compliance with Python documentation standards.

Advanced Features

Real-time Coverage Tracking
Tracks documentation coverage percentage across the entire project.

Complexity Analysis
Calculates cyclomatic complexity for all functions.

Advanced Filtering
Filter functions by documentation status (All, Missing, Documented).

Search Functionality
Locate specific functions across large codebases.

Test Integration
Run pytest test cases directly from the interface with detailed results.

Export Capabilities
Download analysis reports in JSON and CSV formats.

Dashboard Analytics
Visual metrics and insights for overall code quality evaluation.

🧠 Techniques Used
Prompt Engineering

The project uses advanced prompt engineering strategies to ensure accurate and consistent documentation:

Context-Aware Prompts
Function signatures, parameter types, and complexity metrics are included for better understanding.

Style-Specific Instructions
Dedicated prompts for Google, NumPy, and reST formats.

Structured Output Design
Ensures standardized sections such as:

Args

Returns

Raises

Examples

Class-Level Documentation
Specialized prompts generate comprehensive class docstrings describing purpose, attributes, and usage.

LLM-based Text Generation

Transformer-based LLMs accessed via the Groq API are used to:

Analyze function behavior and intent.

Generate detailed and readable docstrings.

Maintain strict documentation style consistency.

Handle complex constructs such as class methods and static methods.

🛠️ Tech Stack
Programming Language

Python 3.8+

Libraries & Frameworks
Web Interface

Streamlit 1.28+

Plotly (data visualization)

Code Analysis

ast (Abstract Syntax Tree parsing)

radon (cyclomatic complexity)

pydocstyle (PEP 257 validation)

LLM Integration

Groq API (transformer-based models)

python-dotenv (environment variable management)

Data Processing

pandas

json

Testing

pytest

pytest-json-report

Utilities

difflib

os, pathlib

🤖 LLM Details
Model Architecture

The project utilizes transformer-based Large Language Models optimized for:

Natural language understanding

Code comprehension

Context-aware documentation generation

Long-range dependency handling

Configurable LLM System

Important: The LLM backend is fully configurable.

Users can:

Switch LLM providers (Groq, OpenAI GPT, Anthropic Claude, local models)

Adjust generation parameters (temperature, max tokens)

Modify model selection in
core/docstring_engine/generator.py

Current Configuration

API Provider: Groq

Configuration Method: Environment variables (GROQ_API_KEY)

Generation Parameters: Tuned for documentation tasks

Fallback Handling: Graceful error handling when API is unavailable

📁 Project Structure
AI_POWERED_CHATBOT/
│
├── ai_powered/
│   ├── cli/
│   │   └── commands.py
│   │
│   ├── core/
│   │   ├── docstring_engine/
│   │   │   └── generator.py
│   │   │
│   │   ├── parser/
│   │   │   └── python_parser.py
│   │   │
│   │   ├── reporter/
│   │   │   └── coverage_reporter.py
│   │   │
│   │   ├── review_engine/
│   │   │   └── ai_review.py
│   │   │
│   │   └── validator/
│   │       └── validator.py
│
├── examples/
│   ├── sample_a.py
│   └── sample_b.py
│
├── storage/
│   ├── reports/
│   └── review_logs.json
│
├── tests/
│   ├── test_parser.py
      └── test_coverage_reporter.py
      └── test_dashboard.py
      └── test_generator.py
      └── test_validator.py

│
├── main_app.py
├── dashboard.py  
├── requirements.txt
├── README.md

🚀 Installation Steps
Prerequisites

Python 3.8+

pip package manager

Groq API key (or alternative LLM credentials)

Step 1: Clone the Repository
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer

Step 2: Create a Virtual Environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

Step 3: Install Dependencies
pip install -r requirements.txt

Step 4: Configure Environment Variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

💻 How to Run the Project Locally
Start the Application
streamlit run main.py


Access the app at: http://localhost:8501

🧭 Usage Workflow
1. Initial Scan

Enter project path

Click Scan Project

Wait for analysis and generation

2. Review Docstrings

Navigate to Docstrings

Compare original vs AI-generated documentation

Accept and apply changes

3. View Metrics

Use Metrics for statistics

Use Dashboard for advanced insights

4. Validate Code

Run PEP 257 Validation

Review violations grouped by file

5. Export Reports

Download JSON or CSV reports from the Dashboard

🧪 Running Tests
pytest
pytest --json-report --json-report-file=storage/reports/pytest_results.json
pytest tests/test_parser.py -v
