from uuid import UUID

class ChatService:
    async def create_chat(
        self, user_id: UUID, new_chat_data: dict
    ) -> None:
        raise NotImplementedError

    def get_chat_history(self):
        raise NotImplementedError

    def build_chat_history(self):
        raise NotImplementedError
