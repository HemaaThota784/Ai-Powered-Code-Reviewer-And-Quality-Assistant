# AI Code Reviewer 🚀

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![LLM](https://img.shields.io/badge/LLM-Groq-purple.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📋 Project Description

AI Code Reviewer is an intelligent documentation analysis and generation tool that leverages Large Language Models (LLMs) to automatically analyze Python codebases, identify missing or incomplete docstrings, and generate high-quality documentation in multiple standard formats. The tool provides an interactive web interface for reviewing, comparing, and applying AI-generated docstrings directly to source code files.

This project demonstrates the practical application of LLM-based text generation for software engineering tasks, specifically addressing the challenge of maintaining comprehensive code documentation across large Python projects.

## ✨ Features

### Core Capabilities
- **Automated Code Scanning**: Recursively analyzes Python projects to extract functions, methods, and classes
- **Multi-Style Docstring Generation**: Generates docstrings in three popular formats:
  - Google Style
  - NumPy Style
  - reStructuredText (reST) Style
- **Interactive Review Workflow**: Side-by-side comparison of existing and AI-generated docstrings
- **Direct File Modification**: Automatically applies accepted docstrings to source files with proper indentation
- **PEP 257 Validation**: Checks code compliance against Python docstring conventions

### Advanced Features
- **Real-time Coverage Tracking**: Monitors documentation coverage percentage across the project
- **Complexity Analysis**: Calculates cyclomatic complexity metrics for all functions
- **Advanced Filtering**: Filter functions by documentation status (All, Missing, Documented)
- **Search Functionality**: Find specific functions across the entire codebase
- **Test Integration**: Run pytest tests directly from the interface with detailed results
- **Export Capabilities**: Download analysis reports in JSON and CSV formats
- **Dashboard Analytics**: Comprehensive metrics and visualizations for code quality insights

## 🧠 Techniques Used

### Prompt Engineering
The project employs sophisticated prompt engineering techniques to ensure high-quality docstring generation:

- **Context-Aware Prompts**: Function signatures, parameter types, and complexity metrics are provided to the LLM for contextual understanding
- **Style-Specific Instructions**: Separate prompts for each docstring style (Google, NumPy, reST) ensure format compliance
- **Structured Output**: Prompts are designed to return well-formatted, consistent docstrings with proper sections (Args, Returns, Raises, Examples)
- **Class Documentation**: Specialized prompts for generating comprehensive class-level docstrings that describe purpose, attributes, and usage

### LLM-based Text Generation
The system utilizes transformer-based Large Language Models through the Groq API to:

1. **Analyze Function Context**: Understand the purpose and behavior of functions from their signatures and structure
2. **Generate Comprehensive Documentation**: Create detailed docstrings including parameter descriptions, return values, exceptions, and usage examples
3. **Maintain Style Consistency**: Ensure all generated docstrings adhere to the selected documentation standard
4. **Handle Complex Scenarios**: Generate appropriate documentation for class methods, static methods, and complex function signatures

## 🛠️ Tech Stack

### Programming Language
- **Python 3.8+**: Core language for all components

### Libraries & Frameworks

#### Web Interface
- **Streamlit 1.28+**: Interactive web application framework
- **Plotly**: Data visualization for metrics and charts

#### Code Analysis
- **ast (Abstract Syntax Tree)**: Python code parsing and analysis
- **radon**: Cyclomatic complexity calculation
- **pydocstyle**: PEP 257 docstring validation

#### LLM Integration
- **Groq API**: Interface to transformer-based language models
- **python-dotenv**: Environment variable management for API keys

#### Data Processing
- **pandas**: Data manipulation and export functionality
- **json**: Report generation and data serialization

#### Testing
- **pytest**: Testing framework
- **pytest-json-report**: JSON test result generation

#### Utilities
- **difflib**: Docstring comparison and diff generation
- **os, pathlib**: File system operations

## 🤖 LLM Details

### Model Architecture
The project utilizes **transformer-based Large Language Models** accessed through the Groq API. These models are specifically designed for:
- Natural language understanding and generation
- Code comprehension and documentation synthesis
- Context-aware text generation with long-range dependencies

### Configurable LLM System
**Important**: The LLM backend is fully configurable and not hardcoded. Users can:
- Switch between different LLM providers by modifying the API integration
- Adjust model parameters (temperature, max tokens, etc.) for different documentation styles
- Use alternative models (OpenAI GPT, Anthropic Claude, local models) by implementing the corresponding API wrapper
- Configure model selection in the `core/docstring_engine/generator.py` module

### Current Configuration
- **API Provider**: Groq
- **Configuration Method**: Environment variable (`GROQ_API_KEY`)
- **Generation Parameters**: Optimized for code documentation tasks
- **Fallback Handling**: Graceful error handling when API is unavailable

## 📁 Project Structure
```
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
│      └── test_coverage_reporter.py
       └── test_dashboard.py
       └── test_generator.py
       └── test_validator.py

│
├── main_app.py
├── dashboard.py  
├── requirements.txt
├── README.md
```

## 🚀 Installation Steps

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Groq API key (or alternative LLM provider credentials)

### Step 1: Clone the Repository
```bash
git clone https://github.com/HemaaThota784/Ai-Powered-Code-Reviewer-And-Quality-Assistant.git
cd ai_powered_chatbot
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

To obtain a Groq API key:
1. Visit [https://console.groq.com](https://console.groq.com)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key

## 💻 How to Run the Project Locally

### Starting the Application
```bash
streamlit run main.py
```

The application will open automatically in your default browser at `http://localhost:8501`

### Usage Workflow

#### 1. Initial Scan
- Enter the path to your Python project in the sidebar (e.g., `examples` or `/path/to/your/project`)
- Click "🔍 Scan Project"
- Wait for the scanning and docstring generation process to complete

#### 2. Review Docstrings
- Navigate to "📝 Docstrings" from the sidebar
- Select a file from the list
- Choose a function to review
- Compare existing and AI-generated docstrings
- Click "✅ Accept & Apply" to update the source file

#### 3. View Metrics
- Navigate to "📈 Metrics" to see complexity analysis and documentation statistics
- Navigate to "📊 Dashboard" for advanced filtering and search capabilities

#### 4. Validate Code
- Navigate to "✅ Validation" to check PEP 257 compliance
- Review violation details grouped by file

#### 5. Export Reports
- From the Dashboard, select "📦 Export"
- Download JSON or CSV reports for further analysis

### Running Tests
```bash
# Run all tests
pytest

# Run tests with JSON report
pytest --json-report --json-report-file=storage/reports/pytest_results.json

# Run specific test file
pytest tests/test_parser.py -v
```

