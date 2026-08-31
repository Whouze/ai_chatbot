from services.gemini_service import GeminiService
from pathlib import Path

from utils.logger import logger

def test_generate_response():
    service = GeminiService()
    image_path = Path(__file__).parent / "image_test" / "piala-dunia-2022.jpeg"
    
    user_input = "Tolong ceritakan tentang gambar ini."
    
    response = service.Handling_TextAndMediaResponse(
        user_id="test_user",
        user_input=user_input,
        file_paths=[str(image_path)],
    )
        
    print(f"[User]: {user_input}")
    print(f"[Bobby]: {response}\n")
        
    assert isinstance(response, str)

if __name__ == "__main__":
    test_generate_response()
