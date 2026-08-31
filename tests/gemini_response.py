from services.gemini_service import GeminiService
from uuid import UUID

from utils.logger import logger

def test_generate_response():
    service = GeminiService()
    while True:
        user_input = input("[USER INPUT]: ")
        
        if user_input.lower() in {"exit", "quit"}:
            logger.info("Exiting test_generate_response.")
            break
        
        response = service.Handling_TextResponse(user_id="test_user", user_input=user_input)
        
        print(f"[User]: {user_input}")
        print(f"[Bobby]: {response}\n")
        
        assert isinstance(response, str)

if __name__ == "__main__":
    test_generate_response()