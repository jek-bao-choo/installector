# Import necessary types from typing module for type hints
from typing import Generator, List, Dict
# Import the completion function from litellm library for LLM interactions
from litellm import completion

# Define function that takes a list of message dictionaries and returns a string generator
def get_llm_response(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    """Stream responses from the LLM"""
    # Make an API call to the LLM with specified model and messages
    response = completion(
        # Use the DeepSeek model via OpenRouter
        model="openrouter/deepseek/deepseek-r1-distill-qwen-32b",
        # Pass the conversation history
        messages=messages,
        # Enable streaming mode for chunk-by-chunk response
        stream=True,
    )
    
    # Iterate through each chunk of the streaming response
    for chunk in response:
        # Check if the chunk contains actual content
        if chunk.choices[0].delta.content is not None:
            # Yield each piece of content as it arrives
            yield chunk.choices[0].delta.content
