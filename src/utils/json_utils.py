"""
JSON utility functions for AI Ad Generator.
"""

import json
import re
from typing import Any, Optional

def extract_json_from_llm_response(response: str, default_value: Any = None) -> Optional[Any]:
    """
    Extract a JSON object or array from an LLM response with better error handling.
    Handles cases where the JSON might be surrounded by text or markdown formatting.
    
    Args:
        response (str): The LLM response text
        default_value: The default value to return if JSON extraction fails
        
    Returns:
        The parsed JSON data or the default value if parsing fails
    """
    # If the response is empty, return the default value
    if not response or not response.strip():
        print("Empty response from LLM.")
        return default_value
    
    # Try different extraction methods
    try:
        # Method 1: Try to parse the entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Look for JSON within code blocks
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        code_blocks = re.findall(code_block_pattern, response)
        if code_blocks:
            for block in code_blocks:
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    continue
        
        # Method 3: Try to find JSON object pattern
        json_object_pattern = r'({[\s\S]*?})'
        object_matches = re.findall(json_object_pattern, response)
        if object_matches:
            # Sort by length (descending) to try the longest match first
            for obj_str in sorted(object_matches, key=len, reverse=True):
                try:
                    return json.loads(obj_str)
                except json.JSONDecodeError:
                    continue
        
        # Method 4: Try to find JSON array pattern
        json_array_pattern = r'(\[[\s\S]*?\])'
        array_matches = re.findall(json_array_pattern, response)
        if array_matches:
            # Sort by length (descending) to try the longest match first
            for arr_str in sorted(array_matches, key=len, reverse=True):
                try:
                    return json.loads(arr_str)
                except json.JSONDecodeError:
                    continue
        
        # If we got here, all extraction methods failed
        print("Failed to extract JSON from LLM response.")
        return default_value
        
    except Exception as e:
        print(f"Unexpected error extracting JSON: {str(e)}")
        return default_value