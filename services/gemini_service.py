from google import genai
from google.genai import types
from google.genai.chats import Chat

from utils.config import settings
from utils.loaders import read_system_prompt
from utils.logger import logger

from services.rag_service import RagService


class GeminiService:
    """Service layer for interacting with the Google GenAI SDK."""

    def __init__(self):
        # Inisialisasi Client resmi SDK baru google-genai
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.system_instruction = read_system_prompt()
        self.config = (
            types.GenerateContentConfig(
                system_instruction=self.system_instruction
            )
            if self.system_instruction
            else None
        )
        self.sessions: dict[str, Chat] = {}  # Dictionary to manage chat sessions per user
        self.rag_service = RagService()

    def Generate_Session(self, user_id: str) -> Chat:
        """Creates or retrieves a chat session for a given user ID."""
        if user_id not in self.sessions:
            self.sessions[user_id] = self.client.chats.create(
                model=settings.GEMINI_MODEL,
                config=self.config
            )
        return self.sessions[user_id]

    def upload_file(self, file_path: str):
        """Uploads a file to Gemini API and returns the file object."""
        # SDK google-genai terbaru bisa langsung menggunakan objek kembalian ini
        return self.client.files.upload(file=file_path)

    def _build_contents(self, user_input: str, file_paths: list[str] | None = None) -> list:
        """Build the contents list with RAG context and optional file uploads."""
        context, score = self.rag_service.retrieve_with_rerank(user_input, threshold=0.65)

        if context:
            logger.info(f"Context retrieved from RAG: {context} with score {score:.4f}")
            final_text = f"Relevant knowledge:\n{context}\n\nUser message:\n{user_input}"
        else:
            logger.info("No relevant context found from RAG. Proceeding with user input only.")
            final_text = user_input

        contents = [final_text]

        if file_paths:
            for path in file_paths:
                uploaded_file = self.upload_file(path)
                contents.append(uploaded_file)

        return contents

    def Handling_GeminiResponse(
        self,
        user_id: str,
        user_input: str,
        file_paths: list[str] | None = None,
    ) -> str:
        """Non-streaming: generates a full response as a string."""
        try:
            logger.info(f"Sending request to Gemini API (non-streaming) for user '{user_id}'...")
            chat = self.Generate_Session(user_id=user_id)
            contents = self._build_contents(user_input, file_paths)
            response = chat.send_message(contents)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response from Gemini API: {e}")
            return "Sorry, I couldn't process your request at the moment."

    def Handling_GeminiStreamResponse(
        self,
        user_id: str,
        user_input: str,
        file_paths: list[str] | None = None,
    ):
        """Streaming: yields response chunks one by one (generator)."""
        try:
            logger.info(f"Sending request to Gemini API (streaming) for user '{user_id}'...")
            chat = self.Generate_Session(user_id=user_id)
            contents = self._build_contents(user_input, file_paths)
            for chunk in chat.send_message_stream(contents):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error generating response from Gemini API: {e}")
            yield "Sorry, I couldn't process your request at the moment."

    def Handling_TextResponse(self, user_id: str, user_input: str) -> str:
        """Backward-compatible text-only response handler."""
        return self.Handling_GeminiResponse(user_id=user_id, user_input=user_input)



# Alias for backward compatibility
GeminiResponseService = GeminiService
