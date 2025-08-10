"""
API module for ASIA.fr Agent
"""

# Only expose FastAPI app to allow `python -m cftravel_py.api`
from .server import app

__all__ = [
    'app',
] 