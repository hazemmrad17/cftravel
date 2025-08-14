"""
Unified Configuration Service for Python
Loads configuration from the centralized config file
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class UnifiedConfig:
    """
    Unified Configuration Manager
    ============================
    Provides centralized access to application configuration.
    Reads from config/app.php and provides fallbacks to environment variables.
    """
    
    def __init__(self):
        # Load environment variables from .env file
        self._load_env_file()
        
        self._config = None
        self._config_file = self._find_config_file()
        self._load_config()
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        # Look for .env file in current directory or parent directories
        current_dir = Path.cwd()
        
        # The .env file is in the project root (parent of cftravel_py)
        project_root = current_dir.parent
        env_file = project_root / '.env'
        if env_file.exists():
            logger.info(f"Loading environment from: {env_file}")
            load_dotenv(env_file)
            return
        
        # Fallback: try other locations
        for path in [current_dir, current_dir.parent, current_dir.parent.parent]:
            env_file = path / '.env'
            if env_file.exists():
                logger.info(f"Loading environment from: {env_file}")
                load_dotenv(env_file)
                return
        
        logger.warning(".env file not found")
    
    def _merge_configs(self, env_config: Dict[str, Any], php_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge environment config with PHP config, prioritizing environment variables"""
        merged = env_config.copy()
        
        # Merge PHP config, but don't override environment variables
        for section, section_data in php_config.items():
            if section not in merged:
                merged[section] = section_data
            elif isinstance(section_data, dict) and isinstance(merged[section], dict):
                # Deep merge for nested dictionaries
                for key, value in section_data.items():
                    if key not in merged[section]:
                        merged[section][key] = value
        
        return merged
    
    def _find_config_file(self) -> Optional[Path]:
        """Find the config/app.php file relative to the project root."""
        # Try to find the config file from the current directory
        current_dir = Path.cwd()
        
        # Look for config/app.php in current directory or parent directories
        for path in [current_dir, current_dir.parent, current_dir.parent.parent]:
            config_file = path / 'config' / 'app.php'
            if config_file.exists():
                logger.info(f"Found config file: {config_file}")
                return config_file
        
        logger.warning("config/app.php not found, will use environment variables")
        return None
    
    def _load_config(self):
        """Load configuration from config/app.php or fallback to environment variables."""
        # Always try to load from environment variables first
        env_config = self._load_from_env()
        
        if self._config_file and self._config_file.exists():
            try:
                # Parse PHP array as JSON-like structure
                php_config = self._parse_php_config(self._config_file)
                # Merge PHP config with environment config, prioritizing environment variables
                self._config = self._merge_configs(env_config, php_config)
                logger.info("Successfully loaded unified configuration from config/app.php and environment")
            except Exception as e:
                logger.error(f"Failed to parse config/app.php: {e}")
                self._config = env_config
        else:
            self._config = env_config
    
    def _parse_php_config(self, config_file: Path) -> Dict[str, Any]:
        """Parse PHP configuration file and convert to Python dict."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the array content from PHP file
            # Find the return statement and extract the array
            start = content.find('return [')
            if start == -1:
                raise ValueError("No return statement found in config file")
            
            # Find the matching closing bracket
            bracket_count = 0
            end = start
            for i, char in enumerate(content[start:], start):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i + 1
                        break
            
            if bracket_count != 0:
                raise ValueError("Unmatched brackets in config file")
            
            # Extract the array content
            array_content = content[start + 7:end - 1]  # Remove 'return [' and ']'
            
            # Convert PHP array to Python dict
            config = self._convert_php_to_python(array_content)
            
            return config
            
        except Exception as e:
            logger.error(f"Error parsing PHP config: {e}")
            raise
    
    def _convert_php_to_python(self, php_content: str) -> Dict[str, Any]:
        """Convert PHP array syntax to Python dict."""
        # This is a simplified parser - in production you might want a more robust solution
        config = {}
        
        # Remove comments
        lines = []
        for line in php_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                lines.append(line)
        
        # Simple key-value parsing
        current_section = None
        for line in lines:
            line = line.strip()
            if not line or line in ['[', ']', ',']:
                continue
            
            # Check if it's a section header
            if line.startswith("'") and line.endswith("' => ["):
                current_section = line[1:-4]  # Remove quotes and ' => ['
                config[current_section] = {}
            elif line.startswith("'") and line.endswith("' => [") and current_section:
                subsection = line[1:-4]
                config[current_section][subsection] = {}
            elif line.startswith("'") and "=>" in line and current_section:
                # Parse key-value pairs
                parts = line.split('=>')
                if len(parts) == 2:
                    key = parts[0].strip().strip("'")
                    value = parts[1].strip().rstrip(',')
                    
                    # Convert value types
                    if value == 'true':
                        value = True
                    elif value == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    
                    if current_section in config:
                        config[current_section][key] = value
        
        return config
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables as fallback."""
        logger.info("Loading configuration from environment variables")
        
        return {
            'environment': os.getenv('ENVIRONMENT', 'local'),
            'debug': os.getenv('DEBUG', 'true').lower() == 'true',
            'servers': {
                'frontend': {
                    'host': '127.0.0.1',
                    'port': int(os.getenv('FRONTEND_PORT', '8001')),
                    'url': f"http://127.0.0.1:{os.getenv('FRONTEND_PORT', '8001')}"
                },
                'backend': {
                    'host': '0.0.0.0',
                    'port': int(os.getenv('API_PORT', '8000')),
                    'url': f"http://localhost:{os.getenv('API_PORT', '8000')}"
                }
            },
            'api': {
                'timeout': int(os.getenv('API_TIMEOUT', '30')),
                'retry_attempts': int(os.getenv('API_RETRY_ATTEMPTS', '3'))
            },
            'cors': {
                'allowed_origins': [
                    'https://ovg-iagent.cftravel.net',
                    'https://iagent.cftravel.net',
                    'http://ovg-iagent.cftravel.net',
                    'http://iagent.cftravel.net',
                    'http://localhost:8000',
                    'http://localhost:8001',
                    'http://localhost:8002',
                    'http://localhost:3000',
                    'http://127.0.0.1:8000',
                    'http://127.0.0.1:8001',
                    'http://127.0.0.1:8002',
                    'http://127.0.0.1:3000'
                ],
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allowed_headers': ['*'],
                'allow_credentials': True
            },
                    'ai': {
                'provider': 'groq',
                'api_key': os.getenv('GROQ_API_KEY'),
                'models': {
                    'reasoning': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 1024,
                        'enabled': True
                    },
                    'generation': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.7,
                        'max_tokens': 2048,
                        'enabled': True
                    },
                    'matcher': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 512,
                        'enabled': True
                    },
                    'extractor': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 1024,
                        'enabled': True
                    }
                }
            }
        }
    
    def get(self, section: str) -> Dict[str, Any]:
        """Get a configuration section."""
        return self._config.get(section, {})
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value."""
        section_data = self.get(section)
        if isinstance(section_data, dict):
            return section_data.get(key, default)
        else:
            # If section_data is not a dict (e.g., string from PHP parser), return default
            return default
    
    def get_server(self, server: str) -> Dict[str, Any]:
        """Get server configuration."""
        servers = self.get('servers')
        if isinstance(servers, dict):
            return servers.get(server, {})
        else:
            # Fallback to environment-based server config
            return {
                'host': '0.0.0.0',
                'port': 8000,
                'url': 'http://localhost:8000'
            }
    
    def get_api(self) -> Dict[str, Any]:
        """Get API configuration."""
        api_config = self.get('api')
        if isinstance(api_config, dict):
            return api_config
        else:
            # Fallback to environment-based API config
            return {
                'timeout': 30,
                'retry_attempts': 3
            }
    
    def get_cors(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        cors_config = self.get('cors')
        if isinstance(cors_config, dict):
            return cors_config
        else:
            # Fallback to environment-based CORS config
            return {
                'allowed_origins': [
                    'https://ovg-iagent.cftravel.net',
                    'https://iagent.cftravel.net',
                    'http://ovg-iagent.cftravel.net',
                    'http://iagent.cftravel.net',
                    'http://localhost:8000',
                    'http://localhost:8001',
                    'http://localhost:8002',
                    'http://localhost:3000',
                    'http://127.0.0.1:8000',
                    'http://127.0.0.1:8001',
                    'http://127.0.0.1:8002',
                    'http://127.0.0.1:3000'
                ],
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allowed_headers': ['*'],
                'allow_credentials': True
            }
    
    def get_ai(self) -> Dict[str, Any]:
        """Get AI configuration."""
        ai_config = self.get('ai')
        if isinstance(ai_config, dict):
            return ai_config
        else:
            # Fallback to environment-based AI config
            return {
                'provider': 'groq',
                'api_key': os.getenv('GROQ_API_KEY'),
                'models': {
                    'reasoning': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 1024,
                        'enabled': True
                    },
                    'generation': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.7,
                        'max_tokens': 2048,
                        'enabled': True
                    },
                    'matcher': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 512,
                        'enabled': True
                    },
                    'extractor': {
                        'name': 'moonshotai/kimi-k2-instruct',
                        'temperature': 0.1,
                        'max_tokens': 1024,
                        'enabled': True
                    }
                }
            }
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self.get_value('environment', 'environment', 'local')
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get_value('environment', 'debug', False)
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.get_environment() == 'production'
    
    def is_local(self) -> bool:
        """Check if running locally."""
        return self.get_environment() == 'local'
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
    
    def log_config(self):
        """Log current configuration for debugging."""
        logger.info("=== UNIFIED CONFIGURATION ===")
        logger.info(f"Environment: {self.get_environment()}")
        logger.info(f"Debug Mode: {self.is_debug()}")
        
        servers = self.get('servers')
        logger.info(f"Frontend: {servers.get('frontend', {}).get('url', 'N/A')}")
        logger.info(f"Backend: {servers.get('backend', {}).get('url', 'N/A')}")
        
        ai_config = self.get('ai')
        logger.info(f"AI Provider: {ai_config.get('provider', 'N/A')}")
        logger.info(f"API Key Set: {'Yes' if ai_config.get('api_key') else 'No'}")
        
        model_switches = ai_config.get('model_switches', {})
        logger.info("Model Switches:")
        for model, enabled in model_switches.items():
            logger.info(f"  {model}: {'ON' if enabled else 'OFF'}")
        
        logger.info("=== END CONFIGURATION ===")

# Global instance
unified_config = UnifiedConfig() 