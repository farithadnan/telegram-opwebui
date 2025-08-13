"""Tests for environment variable loading and validation."""

import os
import sys
from unittest.mock import patch
import pytest

# Add the project root to the path so we can import main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_env_variables_present():
    """Test that environment variables are loaded correctly."""
    # Mock environment variables with valid Telegram token format
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ',
        'OPWEBUI_CHAT_ENDPOINT': 'http://test.example.com',
        'OPWEBUI_JWT_TOKEN': 'test_jwt',
        'OPWEBUI_MODEL': 'test_model',
        'WELCOME_MESSAGE': 'Welcome!',
    }):
        # Remove main from sys.modules if it exists to force re-import
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('main'):
                del sys.modules[module_name]
        
        import main
        
        # Check that variables are loaded correctly
        assert main.TELEGRAM_BOT_TOKEN == '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ'
        assert main.OPWEBUI_CHAT_ENDPOINT == 'http://test.example.com'
        assert main.OPWEBUI_JWT_TOKEN == 'test_jwt'
        assert main.OPWEBUI_MODEL != 'test_model'
        assert main.WELCOME_MESSAGE == 'Welcome!'


def test_missing_env_variables():
    """Test that missing environment variables are detected."""
    # Store original environment
    original_environ = dict(os.environ)
    
    try:
        # Clear all environment variables
        os.environ.clear()
        
        # Remove main from sys.modules if it exists to force re-import
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('main'):
                del sys.modules[module_name]
        
        # Mock the load_dotenv function to prevent loading from file
        with patch('dotenv.load_dotenv'):
            # This should raise SystemExit when main is imported
            with pytest.raises(SystemExit):
                import main
                # Force evaluation
                print(main)
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_environ)