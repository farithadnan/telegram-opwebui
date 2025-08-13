"""Tests for LLM processing functions."""

import sys
import os
from unittest.mock import patch, Mock

# Add the project root to the path so we can import main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import requests
import requests_mock


@pytest.fixture
def mock_response_data():
    """Sample response data from OpenWebUI API."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the AI."
                }
            }
        ]
    }


@pytest.fixture
def mock_response_data_with_text():
    """Sample response data with text field instead of message.content."""
    return {
        "choices": [
            {
                "text": "This is a test response with text field."
            }
        ]
    }


@pytest.fixture
def mock_env_vars():
    """Mock environment variables needed for the LLM processing."""
    return patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ',
        'OPWEBUI_CHAT_ENDPOINT': 'http://test.example.com/api/chat',
        'OPWEBUI_JWT_TOKEN': 'test_token',
        'OPWEBUI_MODEL': 'test_model',
        'OPWEBUI_COLLECTION_ID': 'test_collection',
        'WELCOME_MESSAGE': 'Welcome!',
    })


@pytest.mark.asyncio
async def test_process_with_llm_success(mock_response_data, mock_env_vars):
    """Test successful LLM processing."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                json=mock_response_data,
                status_code=200
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "This is a test response from the AI."


@pytest.mark.asyncio
async def test_process_with_llm_success_text_field(mock_response_data_with_text, mock_env_vars):
    """Test successful LLM processing with text field."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                json=mock_response_data_with_text,
                status_code=200
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "This is a test response with text field."


@pytest.mark.asyncio
async def test_process_with_llm_http_error(mock_env_vars):
    """Test LLM processing with HTTP error."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                status_code=500,
                text='Internal Server Error'
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "Error: AI service returned an error (500)."


@pytest.mark.asyncio
async def test_process_with_llm_timeout(mock_env_vars):
    """Test LLM processing with timeout."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                exc=requests.exceptions.Timeout
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "Error: AI service took too long to respond. Please try again later."


@pytest.mark.asyncio
async def test_process_with_llm_connection_error(mock_env_vars):
    """Test LLM processing with connection error."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                exc=requests.exceptions.ConnectionError
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "Error: Unable to connect to AI service. Please try again later."


@pytest.mark.asyncio
async def test_process_with_llm_invalid_json(mock_env_vars):
    """Test LLM processing with invalid JSON response."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                text='Invalid JSON response',
                status_code=200
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "Error: Received invalid response from AI service."


@pytest.mark.asyncio
async def test_process_with_llm_unexpected_format(mock_env_vars):
    """Test LLM processing with unexpected response format."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        with requests_mock.Mocker() as m:
            m.post(
                'http://test.example.com/api/chat',
                json={"unexpected": "format"},
                status_code=200
            )
            
            result = await main.process_with_llm("Test query", 12345, 67890)
            assert result == "Error: Unexpected response format from AI service."