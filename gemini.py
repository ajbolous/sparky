from google import genai

class LlmClient:
    def generate_content(self, contents: str) -> str:
        raise NotImplementedError(
            "This method should be implemented to call the actual API and return the response text."
        )


class GeminiClient(LlmClient):
    MODEL = "gemini-3-flash-preview"

    def __init__(self, api_key: str):
        self._key = api_key
        self.client = genai.Client(api_key=self._key)

    def generate_content(self, contents: str) -> str:
        response = self.client.models.generate_content(
            model=self.MODEL, contents=contents
        )
        return response.text
