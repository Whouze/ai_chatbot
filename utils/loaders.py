import json
from pathlib import Path
from typing import Any

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


class KnowledgeBaseLoader:
    """Loads knowledge base files from supported formats into text chunks."""

    def __init__(self, supported_types: list[str] | None = None):
        self.supported_types = {
            file_type.lower()
            for file_type in (supported_types or settings.KNOWLEDGE_SUPPORTED_TYPES)
        }

    # ==========================================
    # PUBLIC API
    # ==========================================

    def load(self, file_path: Path | str | None = None) -> list[str]:
        """Load knowledge base from file and return text chunks."""
        target_path = Path(file_path) if file_path else DEFAULT_KNOWLEDGE_PATH

        try:
            if not target_path.exists():
                logger.error(f"Knowledge base file not found at: {target_path}")
                return []

            file_type = self._detect_file_type(target_path)
            if file_type not in self.supported_types:
                logger.warning(f"Unsupported knowledge base file type: {target_path.suffix}")
                return []

            kb_texts = self._load_by_type(target_path, file_type)
            logger.info(f"Loaded {len(kb_texts)} entries from knowledge base: {target_path.name}")
            return kb_texts
        except Exception as e:
            logger.error(f"Error loading knowledge base from {target_path}: {e}")
            return []

    # ==========================================
    # PRIVATE: File Type Detection
    # ==========================================

    def _detect_file_type(self, file_path: Path | str) -> str:
        """Detect knowledge base file type from the file extension."""
        return Path(file_path).suffix.lower().lstrip(".")

    # ==========================================
    # PRIVATE: Router
    # ==========================================

    def _load_by_type(self, file_path: Path, file_type: str) -> list[str]:
        """Route to the appropriate loader based on file type."""
        if file_type == "json":
            return self._load_json(file_path)
        if file_type == "pdf":
            return self._load_pdf(file_path)
        if file_type in {"xlsx", "xls"}:
            return self._load_excel(file_path)
        if file_type == "csv":
            return self._load_csv(file_path)
        return self._load_text(file_path)

    # ==========================================
    # PRIVATE: Loaders per File Type
    # ==========================================

    def _load_json(self, file_path: Path | str) -> list[str]:
        """Load JSON knowledge entries and format them into text chunks."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            data = data.get("items", data.get("data", [data]))

        kb_texts = []
        for item in data:
            if isinstance(item, dict):
                question = item.get("question", "")
                answer = item.get("answer", "")
                category = item.get("category", "")
                content = item.get("content", item.get("text", ""))

                if question or answer or category:
                    text_entry = f"Category: {category}\nQuestion: {question}\nAnswer: {answer}"
                else:
                    text_entry = "\n".join(f"{key}: {value}" for key, value in item.items())

                if content and content not in text_entry:
                    text_entry = f"{text_entry}\nContent: {content}"

                kb_texts.append(text_entry)
            elif isinstance(item, str):
                kb_texts.append(item)

        return [text for text in kb_texts if text.strip()]

    def _load_pdf(self, file_path: Path | str) -> list[str]:
        """Load PDF pages using LangChain's PyPDFLoader."""
        try:
            from langchain_community.document_loaders import PyPDFLoader
        except ImportError as exc:
            raise ImportError(
                "PDF loading requires 'langchain-community' and 'pypdf'. "
                "Install dependencies from requirement.txt."
            ) from exc

        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
        return [doc.page_content.strip() for doc in documents if doc.page_content.strip()]

    def _load_excel(self, file_path: Path | str) -> list[str]:
        """Load Excel sheets and convert each row into a text chunk."""
        pd = self._import_pandas()
        sheets = pd.read_excel(file_path, sheet_name=None)
        kb_texts = []

        for sheet_name, dataframe in sheets.items():
            kb_texts.extend(self._dataframe_to_text_chunks(dataframe, source_name=sheet_name, pandas_module=pd))

        return kb_texts

    def _load_csv(self, file_path: Path | str) -> list[str]:
        """Load CSV rows and convert each row into a text chunk."""
        pd = self._import_pandas()
        dataframe = pd.read_csv(file_path)
        return self._dataframe_to_text_chunks(dataframe, source_name=Path(file_path).name, pandas_module=pd)

    def _load_text(self, file_path: Path | str) -> list[str]:
        """Load plain text or markdown files as paragraph chunks."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = [chunk.strip() for chunk in content.split("\n\n")]
        return [chunk for chunk in chunks if chunk]

    # ==========================================
    # PRIVATE: Helpers
    # ==========================================

    def _import_pandas(self):
        """Import pandas with helpful error message."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "Excel and CSV loading require 'pandas'. "
                "Install dependencies from requirement.txt."
            ) from exc
        return pd

    def _dataframe_to_text_chunks(self, dataframe: Any, source_name: str, pandas_module: Any) -> list[str]:
        """Convert DataFrame rows into text chunks."""
        dataframe = dataframe.dropna(how="all")
        chunks = []

        for _, row in dataframe.iterrows():
            values = [
                f"{column}: {value}"
                for column, value in row.items()
                if pandas_module.notna(value) and str(value).strip()
            ]
            if values:
                chunks.append(f"Source: {source_name}\n" + "\n".join(values))

        return chunks


def load_knowledge_base(file_path: Path | str | None = None) -> list[str]:
    """
    Convenience function for backward compatibility.
    Creates a KnowledgeBaseLoader and loads the knowledge base.
    """
    return KnowledgeBaseLoader().load(file_path)
