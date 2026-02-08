class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []

    def add(self, message: str):
        self.messages.append(message)

    def clear(self):
        self.messages = []

    def get_messages(self):
        return self.messages


class SessionStore:
    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id)
        return self.sessions[session_id]

    def clear_session(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id].clear()
