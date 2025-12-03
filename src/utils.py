"""
utils.py - Shared Utility Functions for Persona AI Project

This module contains helper functions that are used across multiple files
in the project. Import them like:

    from utils import extract_text, safe_json_loads

Functions:
    - extract_text: Safely extracts text from OpenAI API responses
    - safe_json_loads: Cleans and parses JSON from LLM outputs
"""

import json


def extract_text(resp):
    """
    Safely extracts text from any valid OpenAI API response object.

    The OpenAI API has changed over time, so this function tries multiple
    formats to ensure compatibility with different API versions.

    Args:
        resp: The response object from OpenAI API call

    Returns:
        str: The extracted text content, or None if extraction fails

    Example:
        response = client.responses.create(model="gpt-4o-mini", input=[...])
        text = extract_text(response)
        if text:
            print(text)
    """
    # New Responses API format (2024+)
    try:
        return resp.output[0].content[0].text
    except (AttributeError, IndexError, TypeError, KeyError):
        pass

    # ChatCompletion format (standard)
    try:
        return resp.choices[0].message.content
    except (AttributeError, IndexError, TypeError, KeyError):
        pass

    # Alternative ChatCompletion format (dict-style access)
    try:
        return resp.choices[0].message["content"]
    except (AttributeError, IndexError, TypeError, KeyError):
        pass

    # Simple text attribute (some response types)
    try:
        return resp.text
    except AttributeError:
        pass

    return None


def safe_json_loads(text):
    """
    Attempts to parse JSON from LLM output, handling common formatting issues.

    LLMs often return JSON wrapped in Markdown code fences or with extra
    whitespace. This function cleans the text before parsing.

    Args:
        text: Raw text string that should contain JSON

    Returns:
        dict/list: Parsed JSON object, or None if parsing fails

    Example:
        ai_response = '''```json
        {"name": "test", "value": 123}
        ```'''
        data = safe_json_loads(ai_response)
        # Returns: {"name": "test", "value": 123}

    Handles:
        - Markdown code fences (```json ... ```)
        - Extra whitespace
        - "json" label at start of content
    """
    if text is None or text.strip() == "":
        return None

    cleaned = text.strip()

    # Remove Markdown code fences if present (```json ... ```)
    if cleaned.startswith("```"):
        # Remove opening fence and any language identifier
        cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    # Remove "json" label if present at start (sometimes LLMs write "json{...")
    cleaned = cleaned.strip()
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    # Attempt to parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

def format_bool(value):
    """Format boolean values nicely for display."""
    if value is True:
        return "Yes"
    elif value is False:
        return "No"
    elif value == "sometimes":
        return "Sometimes"
    else:
        return "N/A"

def format_scale_value(value, max_value=10):
    """
    Formats a scale value (1-10) as a string with visual indicator.

    Args:
        value: The numeric value (int or float)
        max_value: The maximum value of the scale (default 10)

    Returns:
        str: Formatted string like "7/10" or "N/A" if invalid

    Example:
        format_scale_value(7)  # Returns "7/10"
        format_scale_value(None)  # Returns "N/A"
    """
    if value is None or not isinstance(value, (int, float)):
        return "N/A"
    return f"{int(value)}/{max_value}"


def safe_get(dictionary, *keys, default="N/A"):
    """
    Safely retrieves a nested value from a dictionary.

    Args:
        dictionary: The dict to retrieve from
        *keys: Sequence of keys to traverse
        default: Value to return if key not found (default "N/A")

    Returns:
        The value at the nested key path, or default if not found

    Example:
        data = {"user": {"profile": {"name": "Kai"}}}
        safe_get(data, "user", "profile", "name")  # Returns "Kai"
        safe_get(data, "user", "missing", "key")   # Returns "N/A"
    """
    result = dictionary
    for key in keys:
        try:
            result = result[key]
        except (KeyError, TypeError, IndexError):
            return default
    return result if result is not None else default
