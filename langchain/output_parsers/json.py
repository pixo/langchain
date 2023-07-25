from __future__ import annotations

import json
import re
from json import JSONDecodeError
from typing import Any, List

from langchain.schema import BaseOutputParser, OutputParserException


def is_json(json_string: str) -> bool:
    """
    Check if a string is a valid JSON string.

    Args:
        json_string: The string to check.

    Returns:
        True if the string is a valid JSON string, False otherwise.
    """
    try:
        json_string = json.loads(json_string)
        return json_string
    except json.JSONDecodeError:
        return False


def extract_json(text):
    pattern = f'```json(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    matches = matches[0] if matches else None
    return matches


def parse_json_markdown(json_string: str) -> dict:
    """
    Parse a JSON string from a Markdown string.

    Args:
        json_string: The Markdown string.

    Returns:
        The parsed JSON object as a Python dictionary.
    """
    json_loaded = is_json(json_string)
    if json_loaded:
        return json_loaded

    match = extract_json(json_string)
    if match is None:
        return {'action': 'Final Answer', 'action_input': json_string}
    else:
        json_str = match

    # Strip whitespace and newlines from the start and end
    json_str = json_str.strip()

    # Parse the JSON string into a Python dictionary
    parsed = json.loads(json_str)

    return parsed


def parse_and_check_json_markdown(text: str, expected_keys: List[str]) -> dict:
    """
    Parse a JSON string from a Markdown string and check that it
    contains the expected keys.

    Args:
        text: The Markdown string.
        expected_keys: The expected keys in the JSON string.

    Returns:
        The parsed JSON object as a Python dictionary.
    """
    try:
        json_obj = parse_json_markdown(text)
    except json.JSONDecodeError as e:
        raise OutputParserException(f"Got invalid JSON object. Error: {e}")
    for key in expected_keys:
        if key not in json_obj:
            raise OutputParserException(
                f"Got invalid return object. Expected key `{key}` "
                f"to be present, but got {json_obj}"
            )
    return json_obj


class SimpleJsonOutputParser(BaseOutputParser[Any]):
    def parse(self, text: str) -> Any:
        text = text.strip()
        try:
            return json.loads(text)
        except JSONDecodeError as e:
            raise OutputParserException(f"Invalid json output: {text}") from e

    @property
    def _type(self) -> str:
        return "simple_json_output_parser"
