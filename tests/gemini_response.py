from services.gemini_service import GeminiService
from uuid import UUID
import time

from utils.logger import logger

def test_generate_response():
    service = GeminiService()
    while True:
        time_start = time.time()
        user_input = input("[USER]: ")
        
        if user_input.lower() in {"exit", "quit"}:
            logger.info("Exiting test_generate_response.")
            break
        
        # response = service.Handling_TextResponse(user_id="test_user", user_input=user_input)
        response = service.Handling_GeminiResponse(user_id="test_user", user_input=user_input)
        
        time_end = time.time()
        
        # print(f"[User]: {user_input}")
        print(f"\n[Bobby]: {response}\n")
        
        elapsed_time = (time_end - time_start) * 1000
        print(f"Response generated in {elapsed_time:.2f} ms.")
        
        assert isinstance(response, str)

if __name__ == "__main__":
    test_generate_response()