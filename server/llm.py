from typing import Generator, List, Dict
from litellm import completion

def get_llm_response(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    """Stream responses from the LLM"""
    response = completion(
        model="openrouter/deepseek/deepseek-r1-distill-qwen-32b",
        messages=messages,
        stream=True,
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
