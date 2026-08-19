import sys
from pathlib import Path

# Automatically add project root directory to sys.path for all tests
sys.path.insert(0, str(Path(__file__).resolve().parent))
