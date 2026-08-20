from pathlib import Path
from google import genai
from google.genai import types
from google.genai.chats import Chat

from utils.config import settings
from utils.logger import logger

# Path setup for system prompt file
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
PROMPT_PATH = BASE_DIR / settings.PROMPT_FOLDER / settings.PROMPT_SYSTEM


def read_system_prompt(prompt_path: Path = PROMPT_PATH) -> str | None:
    """Reads system prompt file content. Returns None if empty or missing."""
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return content if content else None
    except FileNotFoundError:
        logger.error(f"Prompt file '{prompt_path}' not found.")
        return None
    except Exception as e:
        logger.error(f"Error reading system prompt file: {e}")
        return None


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

    def Generate_Session(self, user_id: str) -> Chat:
        """Creates or retrieves a chat session for a given user ID."""
        if user_id not in self.sessions:
            self.sessions[user_id] = self.client.chats.create(
                model=settings.GEMINI_MODEL,
                config=self.config
            )
        return self.sessions[user_id]

    def Handling_TextResponse(self, user_id: str, user_input: str) -> str:
        """Generates a response from Gemini API using chat session."""
        try:
            logger.info(f"Sending request to Gemini API via google-genai SDK for user '{user_id}'...")

            chat = self.Generate_Session(user_id=user_id)
            response = chat.send_message(user_input)

            logger.info("Successfully received response from Gemini API.")
            return response.text
        except Exception as e:
            logger.error(f"Error generating response from Gemini API: {e}")
            return "Sorry, I couldn't process your request at the moment."


# Alias for backward compatibility
GeminiResponseService = GeminiService