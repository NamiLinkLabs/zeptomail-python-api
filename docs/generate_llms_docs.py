#!/usr/bin/env python3
"""
Script to generate LLM-friendly documentation from Python code.
This extracts function signatures and docstrings using mkdocstrings.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

def generate_class_docs(module_path: str, class_name: str) -> str:
    """
    Generate markdown documentation for a class, including all methods.
    
    Args:
        module_path: The import path to the module (e.g., 'zeptomail.client')
        class_name: The name of the class to document
        
    Returns:
        Markdown string with class documentation
    """
    # Import the module and get the class
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    
    # Start with class docstring
    doc_parts = [
        f"# {class_name}",
        "",
        inspect.getdoc(cls) or "No class documentation available.",
        "",
        "## Methods",
        ""
    ]
    
    # Get all methods
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Skip private methods (starting with _)
        if name.startswith('_') and name != '__init__':
            continue
            
        # Get the signature
        try:
            signature = inspect.signature(method)
            # For __init__, show it as the class constructor
            if name == '__init__':
                method_sig = f"### {class_name}{signature}"
            else:
                method_sig = f"### {name}{signature}"
        except ValueError:
            method_sig = f"### {name}()"
            
        doc_parts.append(method_sig)
        doc_parts.append("")
        
        # Get the docstring
        docstring = inspect.getdoc(method)
        if docstring:
            doc_parts.append(docstring)
        else:
            doc_parts.append("No documentation available.")
            
        doc_parts.append("")
        doc_parts.append("---")
        doc_parts.append("")
    
    return "\n".join(doc_parts)

def main():
    """Generate LLM-friendly documentation for ZeptoMail client."""
    output_dir = Path(__file__).parent / "api"
    output_dir.mkdir(exist_ok=True)
    
    # Generate documentation for ZeptoMail class
    docs = generate_class_docs("zeptomail.client", "ZeptoMail")
    
    # Add header information
    header = """# ZeptoMail Client API Reference (LLM-friendly)

This document contains the complete API reference for the ZeptoMail client,
formatted specifically for use with Large Language Models (LLMs).

This documentation includes all method signatures and their docstrings,
but excludes implementation details.

"""
    
    # Write to llms.md
    output_file = "llms.md"
    with open(output_file, "w") as f:
        f.write(header + docs)
    
    print(f"Documentation generated at {output_file}")

if __name__ == "__main__":
    main()
