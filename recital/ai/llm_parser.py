import json
from typing import List

from ai.models import StudentPerformance


class LLMResponseError(Exception):
    pass


def parse_llm_recital_response(raw_text: str) -> List[StudentPerformance]:
    """
    Parse and validate the OpenAI recital response into StudentPerformance objects.
    """

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise LLMResponseError("LLM output was not valid JSON") from e

    if not isinstance(data, list):
        raise LLMResponseError("Expected a list of student performances")

    performances: List[StudentPerformance] = []

    for idx, item in enumerate(data):
        try:
            performances.append(StudentPerformance.model_validate(item))
        except Exception as e:
            raise LLMResponseError(f"Invalid student performance at index {idx}") from e

    return performances
