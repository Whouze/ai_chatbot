from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Chatbot API"
    DEBUG: bool = True
    
    DATABASE_URL: str
    
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    
    HASHING_STRING: str
    PROMPT_FOLDER: str
    PROMPT_SYSTEM: str
    
    KNOWLEDGE_FOLDER: str
    KNOWLEDGE_FILE: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="ENV_"
    )

settings = Settings()

    