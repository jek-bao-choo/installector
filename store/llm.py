from litellm import completion

response = completion(
  model="openrouter/deepseek/deepseek-r1-distill-qwen-32b",
  messages = [{ "content": "what model are you? WHat is the name of this model? Are you by OpenAI?","role": "user"}],
  stream=True,
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end='', flush=True)
print()  # Add a newline at the end