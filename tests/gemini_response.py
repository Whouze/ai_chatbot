from services.gemini_service import GeminiService

def test_generate_response():
    service = GeminiService()
    user_input = "Hello, how are you?"
    response = service.generate_response(user_input)
    print(f"\n[USER INPUT]: {user_input}")
    print(f"[GEMINI RESPONSE]: {response}\n")
    assert isinstance(response, str)

if __name__ == "__main__":
    test_generate_response()