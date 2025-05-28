class Session:
    def __init__(self):
        self.chat_history = []

    def add(self, message: list):
        self.chat_history.append(message)

    def get(self) -> list[dict]:
        return self.chat_history
