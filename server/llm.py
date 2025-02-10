from typing import Generator, List, Dict
from litellm import completion
from litellm.exceptions import BudgetExceededError, InvalidRequestError, APIError, RateLimitError

# Define function that takes a list of message dictionaries and returns a string generator
def get_llm_response(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    """Stream responses from the LLM"""
    try:
        response = completion(
            model="openrouter/deepseek/deepseek-r1-distill-qwen-32b",
            messages=messages,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except BudgetExceededError:
        yield "\nError: API budget limit exceeded. Please try again later."
    except RateLimitError:
        yield "\nError: Rate limit reached. Please wait a moment before trying again."
    except InvalidRequestError as e:
        yield f"\nError: Invalid request - {str(e)}"
    except APIError as e:
        yield f"\nError: API error occurred - {str(e)}"
    except Exception as e:
        yield f"\nUnexpected error occurred: {str(e)}"
