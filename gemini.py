import json
import os
from google import genai
from google.genai import types


class LlmClient:
    def generate_content(self, contents: str) -> str:
        raise NotImplementedError(
            "This method should be implemented to call the actual API and return the response text."
        )


class GeminiClient(LlmClient):
    MODEL = "gemini-3-flash-preview"

    def __init__(self, api_key: str):
        self._key = api_key
        self._client = genai.Client(api_key=self._key)

    def generate_content(self, contents: str) -> str:
        response = self._client.models.generate_content(
            model=self.MODEL, contents=contents
        )
        return response.text


class GeminiChatSessions(GeminiClient):
    def __init__(self, config: types.GenerateContentConfig, api_key: str = None):
        super().__init__(api_key)
        self.config = config
        self.sessions = {}

    def _try_load_history(self, session_id: str) -> list[types.Content]:
        path = f"data/sessions/{session_id}.json"
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            raw_history = json.load(f)

    def get_session(self, session_id: str) -> genai.chats.Chat:
        if session_id not in self.sessions:
            history = self._try_load_history(session_id)
            # Use the SDK's native chat creation
            self.sessions[session_id] = self._client.chats.create(
                model=self.MODEL, config=self.config, history=history
            )
        return self.sessions[session_id]

    def save_sessions(self):
        os.makedirs("data/sessions", exist_ok=True)
        for k, session in self.sessions.items():
            serializable_history = []
            for entry in session.history:
                entry_dict = entry.model_dump()
                serializable_history.append(
                    {
                        "role": entry_dict["role"],
                        "content": entry_dict["parts"][0]["text"],
                    }
                )

            with open(f"data/sessions/{k}.json", "w", encoding="utf-8") as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
