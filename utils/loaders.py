import json
from pathlib import Path

from utils.config import settings
from utils.logger import logger

# Base directory for resolving file paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_PATH = BASE_DIR / settings.PROMPT_FOLDER / settings.PROMPT_SYSTEM
DEFAULT_KNOWLEDGE_PATH = BASE_DIR / settings.KNOWLEDGE_FOLDER / settings.KNOWLEDGE_FILE


def read_system_prompt(prompt_path: Path | str | None = None) -> str | None:
    """
    Reads system prompt file content.
    If no prompt_path is provided, defaults to the path configured in settings (.env).
    """
    target_path = Path(prompt_path) if prompt_path else DEFAULT_PROMPT_PATH

    try:
        if not target_path.exists():
            logger.error(f"Prompt file not found at: {target_path}")
            return None

        with open(target_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return content if content else None
    except Exception as e:
        logger.error(f"Error reading system prompt file from {target_path}: {e}")
        return None


def load_knowledge_base(file_path: Path | str | None = None) -> list[str]:
    """
    Loads knowledge base entries from JSON file and formats them into text chunks.
    If no file_path is provided, defaults to the path configured in settings (.env).
    """
    target_path = Path(file_path) if file_path else DEFAULT_KNOWLEDGE_PATH

    try:
        if not target_path.exists():
            logger.error(f"Knowledge base file not found at: {target_path}")
            return []

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        kb_texts = []
        for item in data:
            if isinstance(item, dict):
                question = item.get("question", "")
                answer = item.get("answer", "")
                category = item.get("category", "")
                text_entry = f"Category: {category}\nQuestion: {question}\nAnswer: {answer}"
                kb_texts.append(text_entry)
            elif isinstance(item, str):
                kb_texts.append(item)

        logger.info(f"Loaded {len(kb_texts)} entries from knowledge base: {target_path.name}")
        return kb_texts
    except Exception as e:
        logger.error(f"Error loading knowledge base from {target_path}: {e}")
        return []
