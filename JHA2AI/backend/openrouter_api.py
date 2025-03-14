import os
import json
from openai import OpenAI

class OpenRouterAPI:
    def __init__(self):
        self.api_key = "<your-api-key>"  # Hardcoded API key
        if not self.api_key:
            raise ValueError("The api_key must be set in the configuration.")
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)

    def send_message(self, user_input, model="rekaai/reka-flash-3:free"):
        """Send a message to the OpenRouter API and return the response."""
        completion = self.client.chat.completions.create(model=model, messages=[{"role": "user", "content": user_input}])
        return completion.choices[0].message.content
