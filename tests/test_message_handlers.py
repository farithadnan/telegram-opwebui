"""Tests for message handlers."""

import sys
import os
from unittest.mock import patch, Mock, AsyncMock

# Add the project root to the path so we can import main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from telebot import types

@pytest.fixture
def mock_message():
    """Create a mock message object."""
    message = Mock(spec=types.Message)
    message.from_user = Mock()
    message.from_user.id = 12345
    message.chat = Mock()
    message.chat.id = 67890
    message.text = "Test message"
    message.message_id = 111
    return message

@pytest.fixture
def mock_env_vars():
    """Mock environment variables needed for the message handlers."""
    return patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ',
        'OPWEBUI_CHAT_ENDPOINT': 'http://test.example.com/api/chat',
        'OPWEBUI_JWT_TOKEN': 'test_token',
        'OPWEBUI_MODEL': 'test_model',
        'OPWEBUI_COLLECTION_ID': 'test_collection',
        'WELCOME_MESSAGE': 'Welcome!',
    })

@pytest.mark.asyncio
async def test_send_welcome(mock_message, mock_env_vars):
    """Test the welcome message handler."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main
        
        # Mock the bot.reply_to method
        main.bot.reply_to = AsyncMock()
        
        await main.send_welcome(mock_message)
        main.bot.reply_to.assert_called_once()

@pytest.mark.asyncio
async def test_handle_message(mock_message, mock_env_vars):
    """Test the message handler."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        # Mock the process_with_llm function, bot.reply_to method, and bot.send_chat_action
        main.process_with_llm = AsyncMock(return_value="Test response")
        main.bot.reply_to = AsyncMock()
        main.bot.send_chat_action = AsyncMock()

        await main.handle_message(mock_message)
        main.process_with_llm.assert_called_once_with("Test message", 12345, 67890)
        main.bot.reply_to.assert_called_once_with(mock_message, "Test response")
        main.bot.send_chat_action.assert_called_once_with(67890, "typing")

@pytest.mark.asyncio
async def test_handle_message_with_error(mock_message, mock_env_vars):
    """Test the message handler with error."""
    with mock_env_vars:
        # Re-import main to pick up the mocked environment
        if 'main' in sys.modules:
            del sys.modules['main']
        import main

        # Mock the process_with_llm function to raise an exception
        main.process_with_llm = AsyncMock(side_effect=Exception("Test error"))
        main.bot.reply_to = AsyncMock()
        main.bot.send_chat_action = AsyncMock()

        await main.handle_message(mock_message)
        main.process_with_llm.assert_called_once_with("Test message", 12345, 67890)
        main.bot.reply_to.assert_called_once()
        main.bot.send_chat_action.assert_called_once_with(67890, "typing")