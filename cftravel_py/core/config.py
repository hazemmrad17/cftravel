"""
Modular configuration for ASIA.fr Travel Agent
Uses Groq models for all LLM operations - fully configurable via environment variables
"""

import os
from pathlib import Path
from typing import List

class Config:
    """Centralized configuration for ASIA.fr Agent"""
    
    def __init__(self):
        self._detect_environment()
        self._setup_config()
    
    def _detect_environment(self):
        """Detect if we're running in production or development"""
        # Check for production indicators
        self.is_production = any([
            os.getenv('NODE_ENV') == 'production',
            os.getenv('ENVIRONMENT') == 'production',
            'cftravel.net' in os.getenv('HOSTNAME', ''),
            'asia-iagent.cftravel.net' in os.getenv('HOSTNAME', ''),
            'ovg-iagent.cftravel.net' in os.getenv('HOSTNAME', ''),
            os.path.exists('/var/www'),  # Common production path
            os.path.exists('/var/repo'),  # Git repo path
            os.getenv('PORT') == '8000'  # Production port
        ])
        
        # Check for development indicators
        self.is_development = any([
            os.getenv('NODE_ENV') == 'development',
            os.getenv('ENVIRONMENT') == 'development',
            'localhost' in os.getenv('HOSTNAME', ''),
            '127.0.0.1' in os.getenv('HOSTNAME', ''),
            os.getenv('PORT') == '8002'  # Development port
        ])
        
        # Default to development if unclear
        if not self.is_production and not self.is_development:
            self.is_development = True
    
    def _setup_config(self):
        """Setup configuration based on environment"""
        if self.is_production:
            self._setup_production()
        else:
            self._setup_development()
    
    def _setup_production(self):
        """Production configuration"""
        self.API_PORT = 8000
        self.API_HOST = "0.0.0.0"
        
        # Auto-detect domain from environment or file system
        hostname = os.getenv('HOSTNAME', '')
        current_path = os.getcwd()
        
        # Check if we're in the Asia domain
        if ('asia-iagent.cftravel.net' in hostname or 
            'asia' in current_path.lower() or
            os.path.exists('/var/www/asia-iagent.cftravel.net')):
            self.BASE_URL = "https://asia-iagent.cftravel.net"
            self.DOMAIN = "asia-iagent.cftravel.net"
        else:
            self.BASE_URL = "https://ovg-iagent.cftravel.net"
            self.DOMAIN = "ovg-iagent.cftravel.net"
        
        self.ALLOWED_ORIGINS = [
            "https://asia-iagent.cftravel.net",
            "https://ovg-iagent.cftravel.net",
            "https://iagent.cftravel.net"
        ]
        self.DEBUG = False
        self.LOG_LEVEL = "INFO"
        
    def _setup_development(self):
        """Development configuration"""
        self.API_PORT = 8002
        self.API_HOST = "0.0.0.0"
        self.BASE_URL = "http://localhost:8002"
        self.ALLOWED_ORIGINS = [
            "http://localhost:8000",
            "http://localhost:8002",
            "http://localhost:3000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8002",
            "http://127.0.0.1:3000"
        ]
        self.DEBUG = True
        self.LOG_LEVEL = "DEBUG"
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins for current environment"""
        return self.ALLOWED_ORIGINS
    
    @property
    def server_config(self) -> dict:
        """Get server configuration"""
        return {
            "host": self.API_HOST,
            "port": self.API_PORT,
            "debug": self.DEBUG
        }
    
    def get_logging_config(self) -> dict:
        """Get logging configuration"""
        return {
            "level": self.LOG_LEVEL,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }

# Global configuration instance
config = Config()

# Export commonly used values
API_PORT = config.API_PORT
API_HOST = config.API_HOST
BASE_URL = config.BASE_URL
ALLOWED_ORIGINS = config.ALLOWED_ORIGINS
DEBUG = config.DEBUG
LOG_LEVEL = config.LOG_LEVEL 