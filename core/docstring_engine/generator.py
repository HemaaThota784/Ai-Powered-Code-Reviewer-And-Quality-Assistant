"""
core.docstring_engine.generator

Generate docstrings in multiple styles (Google, NumPy, reST) using Groq LLM.
Enhanced to generate docstrings for all functions AND classes regardless of existing documentation.
"""

import os
from typing import Dict, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


def _arg_type_str(arg: Dict, style: str = "google") -> str:
    """Format argument with type annotation for docstring."""
    if style == "numpy":
        if arg.get("annotation"):
            return f"{arg['name']} : {arg['annotation']}"
        return arg["name"]
    elif style == "rest":
        if arg.get("annotation"):
            return f":param {arg['annotation']} {arg['name']}:"
        return f":param {arg['name']}:"
    else:  # google
        if arg.get("annotation"):
            return f"{arg['name']} ({arg['annotation']})"
        return arg["name"]


def _build_prompt(func_meta: Dict, style: str = "google") -> str:
    """
    Build a prompt for Groq to generate a docstring in specified style.
    
    Args:
        func_meta (Dict): Function metadata dictionary
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Formatted prompt for the LLM
    """
    func_name = func_meta['name']
    args = func_meta.get('args', [])
    returns = func_meta.get('returns')
    raises = func_meta.get('raises', [])
    existing_docstring = func_meta.get('docstring', '')
    
    # Filter out self and cls
    filtered_args = [arg for arg in args if arg['name'] not in ('self', 'cls')]
    
    style_examples = {
        "google": """
Example Google style:
\"\"\"
Brief description.

Args:
    param1 (int): Description of param1
    param2 (str): Description of param2

Returns:
    bool: Description of return value

Raises:
    ValueError: When something goes wrong
\"\"\"

Note: Only include sections that are relevant. If there are no exceptions, omit the Raises section entirely.""",
        "numpy": """
Example NumPy style:
\"\"\"
Brief description.

Parameters
----------
param1 : int
    Description of param1
param2 : str
    Description of param2

Returns
-------
bool
    Description of return value

Raises
------
ValueError
    When something goes wrong
\"\"\"

Note: Only include sections that are relevant. If there are no exceptions, omit the Raises section entirely.""",
        "rest": """
Example reST style:
\"\"\"
Brief description.

:param int param1: Description of param1
:param str param2: Description of param2
:returns: Description of return value
:rtype: bool
:raises ValueError: When something goes wrong
\"\"\"

Note: Only include sections that are relevant. If there are no exceptions, omit the raises section entirely."""
    }
    
    # Build context about existing documentation
    existing_doc_context = ""
    if existing_docstring and existing_docstring.strip() != '"""\nNo docstring.\n"""':
        existing_doc_context = f"\n\nExisting docstring (for reference):\n{existing_docstring}"
    
    # Only mention raises if there actually are exceptions
    if raises:
        raises_info = f"- Raises: {', '.join(raises)} (YOU MUST include a Raises section)"
    else:
        raises_info = "- Raises: None (DO NOT include a Raises section)"

    
    prompt = f"""Generate a {style.upper()}-style docstring for a Python function named '{func_name}'.

Function signature details:
- Arguments: {', '.join([f"{arg['name']}: {arg.get('annotation', 'Any')}" for arg in filtered_args]) if filtered_args else 'None'}
- Returns: {returns if returns else 'None'}
{raises_info}{existing_doc_context}

{style_examples.get(style, style_examples['google'])}

Requirements:
1. Start with a clear, concise summary line
2. Follow {style.upper()}-style formatting strictly
3. Include only relevant sections (Args/Parameters, Returns, and Raises ONLY if exceptions exist)
4. Use proper indentation
5. Do NOT include the triple quotes in your response
6. Be descriptive but concise
7. Exclude self/cls parameters
8. Generate a COMPLETE docstring even if one already exists
9. If an existing docstring is provided, use its content as context but reformat to {style.upper()} style
10. IMPORTANT: If there are no exceptions (Raises: None), do NOT include a Raises section at all

Generate only the docstring content (without the triple quotes):"""
    
    return prompt


def _build_class_prompt(class_meta: Dict, style: str = "google") -> str:
    """
    Build a prompt for Groq to generate a CLASS docstring in specified style.
    
    Args:
        class_meta (Dict): Class metadata dictionary
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Formatted prompt for the LLM
    """
    class_name = class_meta['name']
    methods = class_meta.get('methods', [])
    existing_docstring = class_meta.get('docstring', '')
    
    # Get method names and their brief purpose
    method_list = ', '.join([m['name'] for m in methods if m['name'] not in ('__init__', '__str__', '__repr__')])
    
    style_examples = {
        "google": """
Example Google style for classes:
\"\"\"
Brief description of the class.

This class provides functionality for... [more detailed description if needed]

Attributes:
    attr1 (str): Description of attribute 1
    attr2 (int): Description of attribute 2
\"\"\"

Note: Only include Attributes section if the class has notable attributes.""",
        "numpy": """
Example NumPy style for classes:
\"\"\"
Brief description of the class.

This class provides functionality for... [more detailed description if needed]

Attributes
----------
attr1 : str
    Description of attribute 1
attr2 : int
    Description of attribute 2
\"\"\"

Note: Only include Attributes section if the class has notable attributes.""",
        "rest": """
Example reST style for classes:
\"\"\"
Brief description of the class.

This class provides functionality for... [more detailed description if needed]

.. attribute:: attr1
    :type: str
    
    Description of attribute 1

.. attribute:: attr2
    :type: int
    
    Description of attribute 2
\"\"\"

Note: Only include attributes if the class has notable attributes."""
    }
    
    # Build context about existing documentation
    existing_doc_context = ""
    if existing_docstring and existing_docstring.strip() != '"""\nNo docstring.\n"""':
        existing_doc_context = f"\n\nExisting docstring (for reference):\n{existing_docstring}"
    
    prompt = f"""Generate a {style.upper()}-style docstring for a Python class named '{class_name}'.

Class details:
- Class name: {class_name}
- Methods: {method_list if method_list else 'None (empty class)'}
- Number of methods: {len(methods)}{existing_doc_context}

{style_examples.get(style, style_examples['google'])}

Requirements:
1. Start with a clear, concise summary line describing the class purpose
2. Follow {style.upper()}-style formatting strictly
3. Provide a brief overview of what the class does
4. Only include Attributes section if it makes sense for the class
5. Use proper indentation
6. Do NOT include the triple quotes in your response
7. Be descriptive but concise
8. Generate a COMPLETE docstring even if one already exists
9. Focus on the class's PURPOSE and RESPONSIBILITY, not implementation details

Generate only the docstring content (without the triple quotes):"""
    
    return prompt


def generate_google_docstring(func_meta: Dict, use_groq: bool = True, style: str = "google") -> str:
    """
    Generate a docstring for a function using Groq LLM via LangChain.
    
    This function ALWAYS generates a new docstring regardless of whether one exists.
    It will generate docstrings for functions that:
    - Have no docstring
    - Have an existing docstring in any style
    
    Args:
        func_meta (Dict): Function metadata dictionary containing name, args, returns, etc.
        use_groq (bool): Whether to use Groq LLM or fallback to template
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Complete docstring with triple quotes
    """
    print(f"[DEBUG] Generating {style} docstring for: {func_meta.get('name', 'unknown')}")
    
    if not use_groq:
        print(f"[INFO] Using fallback template generation (use_groq=False)")
        return _generate_fallback_docstring(func_meta, style)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(f"[WARNING] GROQ_API_KEY not found. Using fallback template for {style} style.")
        return _generate_fallback_docstring(func_meta, style)
    
    print(f"[DEBUG] API Key found: {api_key[:10]}...")
    
    try:
        # 1️⃣ Initialize LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500,
            groq_api_key=api_key
        )
        
        # 2️⃣ Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"You are a Python documentation expert. Generate clear, accurate {style.upper()}-style docstrings following the exact format conventions. Always generate a complete docstring regardless of existing documentation."),
            ("user", "{prompt_text}")
        ])
        
        # 3️⃣ Create output parser
        output_parser = StrOutputParser()
        
        # 4️⃣ Build the chain
        chain = prompt_template | llm | output_parser
        
        # 5️⃣ Add fallback chain
        fallback_chain = RunnableLambda(lambda x: _generate_fallback_docstring(func_meta, style))
        chain_with_fallback = chain.with_fallbacks([fallback_chain])
        
        # 6️⃣ Build prompt
        prompt_text = _build_prompt(func_meta, style)
        print(f"[DEBUG] Prompt built, length: {len(prompt_text)}")
        
        # 7️⃣ Invoke chain
        print(f"[DEBUG] Calling Groq API via LangChain...")
        docstring_content = chain_with_fallback.invoke({"prompt_text": prompt_text})
        print(f"[DEBUG] API call successful")
        
        print(f"[DEBUG] Docstring content length: {len(docstring_content)}")
        
        # 8️⃣ Clean up response
        # Remove markdown code blocks if present
        if docstring_content.startswith("```"):
            lines = docstring_content.split('\n')
            docstring_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else docstring_content
        
        # Remove triple quotes if they were included
        docstring_content = docstring_content.strip('"""').strip("'''").strip()
        
        # 9️⃣ Wrap in triple quotes
        result = f'"""\n{docstring_content}\n"""'
        print(f"[DEBUG] Final docstring generated successfully")
        return result
        
    except Exception as e:
        print(f"[ERROR] Error generating docstring with LangChain: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        print(f"[INFO] Falling back to template-based generation for {style} style.")
        return _generate_fallback_docstring(func_meta, style)


def generate_class_docstring(class_meta: Dict, use_groq: bool = True, style: str = "google") -> str:
    """
    Generate a docstring for a CLASS using Groq LLM via LangChain.
    
    This function ALWAYS generates a new class docstring regardless of whether one exists.
    
    Args:
        class_meta (Dict): Class metadata dictionary containing name, methods, etc.
        use_groq (bool): Whether to use Groq LLM or fallback to template
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Complete docstring with triple quotes
    """
    print(f"[DEBUG] Generating {style} CLASS docstring for: {class_meta.get('name', 'unknown')}")
    
    if not use_groq:
        print(f"[INFO] Using fallback template generation for class (use_groq=False)")
        return _generate_fallback_class_docstring(class_meta, style)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(f"[WARNING] GROQ_API_KEY not found. Using fallback template for {style} style.")
        return _generate_fallback_class_docstring(class_meta, style)
    
    print(f"[DEBUG] API Key found: {api_key[:10]}...")
    
    try:
        # 1️⃣ Initialize LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=400,
            groq_api_key=api_key
        )
        
        # 2️⃣ Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"You are a Python documentation expert. Generate clear, accurate {style.upper()}-style CLASS docstrings following the exact format conventions. Focus on describing the class purpose and responsibility."),
            ("user", "{prompt_text}")
        ])
        
        # 3️⃣ Create output parser
        output_parser = StrOutputParser()
        
        # 4️⃣ Build the chain
        chain = prompt_template | llm | output_parser
        
        # 5️⃣ Add fallback chain
        fallback_chain = RunnableLambda(lambda x: _generate_fallback_class_docstring(class_meta, style))
        chain_with_fallback = chain.with_fallbacks([fallback_chain])
        
        # 6️⃣ Build prompt
        prompt_text = _build_class_prompt(class_meta, style)
        print(f"[DEBUG] Class prompt built, length: {len(prompt_text)}")
        
        # 7️⃣ Invoke chain
        print(f"[DEBUG] Calling Groq API for class via LangChain...")
        docstring_content = chain_with_fallback.invoke({"prompt_text": prompt_text})
        print(f"[DEBUG] API call successful")
        
        print(f"[DEBUG] Class docstring content length: {len(docstring_content)}")
        
        # 8️⃣ Clean up response
        if docstring_content.startswith("```"):
            lines = docstring_content.split('\n')
            docstring_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else docstring_content
        
        docstring_content = docstring_content.strip('"""').strip("'''").strip()
        
        # 9️⃣ Wrap in triple quotes
        result = f'"""\n{docstring_content}\n"""'
        print(f"[DEBUG] Final class docstring generated successfully")
        return result
        
    except Exception as e:
        print(f"[ERROR] Error generating class docstring with LangChain: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        print(f"[INFO] Falling back to template-based generation for {style} style.")
        return _generate_fallback_class_docstring(class_meta, style)

def _generate_fallback_docstring(func_meta: Dict, style: str = "google") -> str:
    """
    Generate a template-based docstring in specified style (fallback method).
    
    This is used when Groq API is unavailable or fails.
    
    Args:
        func_meta (Dict): Function metadata dictionary
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Complete docstring
    """
    lines = ['"""']
    func_name = func_meta['name']
    args = func_meta.get("args", [])
    returns = func_meta.get("returns")
    raises = func_meta.get("raises", [])
    
    # Filter out self and cls
    filtered_args = [arg for arg in args if arg["name"] not in ("self", "cls")]
    
    # Summary line
    lines.append(f"Short description of `{func_name}`.")
    
    if filtered_args or returns or raises:
        lines.append("")
    
    if style == "numpy":
        # NumPy style
        if filtered_args:
            lines.append("Parameters")
            lines.append("----------")
            for arg in filtered_args:
                ann = arg.get("annotation", "TYPE")
                lines.append(f"{arg['name']} : {ann}")
                lines.append(f"    Description of {arg['name']}.")
                if arg != filtered_args[-1]:
                    lines.append("")
        
        if returns and returns != "None":
            if filtered_args:
                lines.append("")
            lines.append("Returns")
            lines.append("-------")
            lines.append(returns)
            lines.append("    Description of return value.")
        
        # Only add Raises section if there are actual exceptions
        if raises:
            if filtered_args or returns:
                lines.append("")
            lines.append("Raises")
            lines.append("------")
            for exc in raises:
                lines.append(exc)
                lines.append(f"    Description of when {exc} is raised.")
                if exc != raises[-1]:
                    lines.append("")
    
    elif style == "rest":
        # reST style
        if filtered_args:
            for arg in filtered_args:
                ann = arg.get("annotation", "TYPE")
                lines.append(f":param {ann} {arg['name']}: Description of {arg['name']}.")
        
        if returns and returns != "None":
            if filtered_args:
                lines.append("")
            lines.append(f":returns: Description of return value.")
            lines.append(f":rtype: {returns}")
        
        # Only add raises if there are actual exceptions
        if raises:
            if filtered_args or returns:
                lines.append("")
            for exc in raises:
                lines.append(f":raises {exc}: Description of when {exc} is raised.")
    
    else:
        # Google style (default)
        if filtered_args:
            lines.append("Args:")
            for arg in filtered_args:
                arg_str = _arg_type_str(arg, "google")
                lines.append(f"    {arg_str}: Description of {arg['name']}.")
        
        if returns and returns != "None":
            if filtered_args:
                lines.append("")
            lines.append("Returns:")
            lines.append(f"    {returns}: Description of return value.")
        
        # Only add Raises section if there are actual exceptions
        if raises:
            if filtered_args or returns:
                lines.append("")
            lines.append("Raises:")
            for exc in raises:
                lines.append(f"    {exc}: Description of when {exc} is raised.")
    
    lines.append('"""')
    return "\n".join(lines)


def _generate_fallback_class_docstring(class_meta: Dict, style: str = "google") -> str:
    """
    Generate a template-based CLASS docstring in specified style (fallback method).
    
    This is used when Groq API is unavailable or fails.
    
    Args:
        class_meta (Dict): Class metadata dictionary
        style (str): Docstring style - 'google', 'numpy', or 'rest'
        
    Returns:
        str: Complete class docstring
    """
    lines = ['"""']
    class_name = class_meta['name']
    methods = class_meta.get('methods', [])
    
    # Summary line
    lines.append(f"Class for {class_name}.")
    lines.append("")
    lines.append(f"This class provides functionality through {len(methods)} method(s).")
    
    lines.append('"""')
    return "\n".join(lines)


def generate_all_styles(func_meta: Dict, use_groq: bool = True) -> Dict[str, str]:
    """
    Generate docstrings in all supported styles for a function.
    
    This is a convenience function that generates docstrings in Google, NumPy,
    and reST styles all at once.
    
    Args:
        func_meta (Dict): Function metadata dictionary
        use_groq (bool): Whether to use Groq LLM or fallback to template
        
    Returns:
        Dict[str, str]: Dictionary with keys 'google', 'numpy', 'rest' and
                       their corresponding docstrings
    """
    return {
        "google": generate_google_docstring(func_meta, use_groq=use_groq, style="google"),
        "numpy": generate_google_docstring(func_meta, use_groq=use_groq, style="numpy"),
        "rest": generate_google_docstring(func_meta, use_groq=use_groq, style="rest")
    }


def generate_all_styles_class(class_meta: Dict, use_groq: bool = True) -> Dict[str, str]:
    """
    Generate CLASS docstrings in all supported styles.
    
    This is a convenience function that generates class docstrings in Google, NumPy,
    and reST styles all at once.
    
    Args:
        class_meta (Dict): Class metadata dictionary
        use_groq (bool): Whether to use Groq LLM or fallback to template
        
    Returns:
        Dict[str, str]: Dictionary with keys 'google', 'numpy', 'rest' and
                       their corresponding class docstrings
    """
    return {
        "google": generate_class_docstring(class_meta, use_groq=use_groq, style="google"),
        "numpy": generate_class_docstring(class_meta, use_groq=use_groq, style="numpy"),
        "rest": generate_class_docstring(class_meta, use_groq=use_groq, style="rest")
    }
