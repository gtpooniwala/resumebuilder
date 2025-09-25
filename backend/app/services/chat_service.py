from fastapi import HTTPException

class ChatService:
    def __init__(self):
        self.chat_history = []

    def add_message(self, user_message: str):
        self.chat_history.append({"role": "user", "content": user_message})

    def get_response(self):
        # TODO: Implement logic to generate a response based on chat history
        return "This is a placeholder response."

    def get_chat_history(self):
        return self.chat_history

# Example usage
# chat_service = ChatService()
# chat_service.add_message("How can I improve my resume?")
# response = chat_service.get_response()
# print(response)  # This will print the placeholder response.