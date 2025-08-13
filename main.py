"""Telegram bot integrating with OpenWebUI LLM API."""

import os
import json
import time
import asyncio
import logging

from pathlib import Path

import requests
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

# Configure logging
# Create logs directory if it doesn't exist
root_dir = Path(__file__).resolve().parent
logs_dir = root_dir / 'logs'
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "telebot-opwebui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("telebot-opwebui")

# Load environment variables from .env file
load_dotenv(root_dir / 'config' / '.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPWEBUI_CHAT_ENDPOINT = os.getenv('OPWEBUI_CHAT_ENDPOINT')
OPWEBUI_JWT_TOKEN = os.getenv('OPWEBUI_JWT_TOKEN')
OPWEBUI_MODEL = os.getenv('OPWEBUI_MODEL')
OPWEBUI_COLLECTION_ID = os.getenv('OPWEBUI_COLLECTION_ID')

# Configurable message
WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')

# Validate required environment variables
missing_vars = []
if not TELEGRAM_BOT_TOKEN:
    missing_vars.append('TELEGRAM_BOT_TOKEN')
if not OPWEBUI_CHAT_ENDPOINT:
    missing_vars.append('OPWEBUI_CHAT_ENDPOINT')
if not OPWEBUI_JWT_TOKEN:
    missing_vars.append('OPWEBUI_JWT_TOKEN')
if not OPWEBUI_MODEL:
    missing_vars.append('OPWEBUI_MODEL')
if not WELCOME_MESSAGE:
    missing_vars.append('WELCOME_MESSAGE')
if not SYSTEM_PROMPT:
    missing_vars.append('SYSTEM_PROMPT')

if missing_vars:
    logger.error("Missing required environment variables: %s", ", ".join(missing_vars))
    exit(1)

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    """Send a welcome message to the user"""
    logger.info(
        "User %s started conversation. Chat ID: %s",
        message.from_user.id,
        message.chat.id
    )

    help_text = f"""
        {WELCOME_MESSAGE}

        Available commands:
        /start - Start the bot
        /help - Show this help message

        Just send me any question and I'll answer it using {OPWEBUI_MODEL} model!
    """

    await bot.reply_to(message, help_text)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    """Handle all other messages as queries"""
    user_id = message.from_user.id
    query = message.text.strip()
    message_id = message.message_id
    chat_id = message.chat.id

    logger.info(
        "Received message from user %s in chat %s. Message ID: %s. Content: %s",
        user_id,
        chat_id,
        message_id,
        query[:50] + ('...' if len(query) > 50 else '')
    )
    await bot.send_chat_action(message.chat.id, "typing")

    start_time = time.time()
    try:
        llm_response = await process_with_llm(query, user_id, chat_id)
        processing_time = time.time() - start_time

        logger.info(
            "Successfully processed message from user %s. Processing time: %.2fs. Response: %s",
            user_id,
            processing_time,
            llm_response[:100] + ('...' if len(llm_response) > 100 else '')
        )
        await bot.reply_to(message, llm_response)

    except (asyncio.CancelledError, RuntimeError, ValueError) as e:
        processing_time = time.time() - start_time
        logger.error(
            "Error processing message from user %s after %.2fs: %s", 
            user_id,
            processing_time,
            e
        )
        await bot.reply_to(message, "Sorry, something went wrong. Please try again later.")
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Unexpected error processing message from user %s after %.2fs: %s", 
            user_id,
            processing_time,
            e
        )
        await bot.reply_to(message, "Sorry, something went wrong. Please try again later.")

async def process_with_llm(query: str,  user_id: int = None, chat_id: int = None) -> str:
    """Process a query using the LLM"""
    logger.debug(
        "Processing query for user %s in chat %s: %s",
        user_id,
        chat_id,
        query[:50] + ('...' if len(query) > 50 else '')
    )

    headers = {
        "Authorization": f"Bearer {OPWEBUI_JWT_TOKEN}",
        "Content-Type": "application/json"
    }

    start_time = time.time()
    try:
        logger.debug(
            "Sending request to OpenWebUI API at %s for user %s",
            OPWEBUI_CHAT_ENDPOINT,
            user_id
        )
        response = requests.post(
            OPWEBUI_CHAT_ENDPOINT,
            headers=headers,
            json={
                "model": OPWEBUI_MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                "files": [
                    {"type": "collection", "id": OPWEBUI_COLLECTION_ID}
                ]
            },
            timeout=30
        )

        api_response_time = time.time() - start_time
        logger.debug(
            "Received response from OpenWebUI API in %.2fs for user %s. Status code: %s",
            api_response_time,
            user_id,
            response.status_code
        )

        response.raise_for_status()
        response_json = response.json()
        logger.debug(
            "Response JSON structure for user %s: %s",
            user_id,
            list(response_json.keys()) if isinstance(response_json, dict) else 'Not a dict'
        )

    except requests.exceptions.ConnectionError:
        api_response_time = time.time() - start_time
        logger.error(
            "Connection error to OpenWebUI at %s for user %s after %.2fs",
            OPWEBUI_CHAT_ENDPOINT,
            user_id,
            api_response_time
        )
        return "Error: Unable to connect to AI service. Please try again later."
    except requests.exceptions.Timeout:
        api_response_time = time.time() - start_time
        logger.error(
            "Timeout connecting to OpenWebUI for user %s after %.2fs",
            user_id,
            api_response_time
        )
        return "Error: AI service took too long to respond. Please try again later."
    except requests.exceptions.HTTPError as e:
        api_response_time = time.time() - start_time
        logger.error(
            "HTTP error from OpenWebUI for user %s after %.2fs: %s. Status code: %s",
            user_id,
            api_response_time,
            e,
            e.response.status_code
        )
        return f"Error: AI service returned an error ({e.response.status_code})."
    except json.JSONDecodeError:
        api_response_time = time.time() - start_time
        logger.error(
            "Invalid JSON response from OpenWebUI for user %s after %.2fs",
            user_id,
            api_response_time
        )
        return "Error: Received invalid response from AI service."
    except requests.exceptions.RequestException as e:
        api_response_time = time.time() - start_time
        logger.error(
            "RequestException processing query for user %s after %.2fs: %s",
            user_id,
            api_response_time,
            e
        )
        return "Error: A network error occurred while contacting the AI service."

    # Extract LLM response
    llm_response = ""
    if 'choices' in response_json and len(response_json['choices']) > 0:
        choice = response_json['choices'][0]
        if 'message' in choice and 'content' in choice['message']:
            llm_response = choice['message']['content']
        elif 'text' in choice:
            llm_response = choice['text']
    else:
        logger.warning(
            "Unexpected response format from OpenWebUI: %s", 
            response_json
        )
        return "Error: Unexpected response format from AI service."

    logger.debug(
        "Extracted LLM response for user %s: %s%s",
        user_id,
        llm_response[:100],
        "..." if len(llm_response) > 100 else ""
    )

    return llm_response

async def main():
    """
    Main entry point for the application.
    """
    logger.info("Starting Telebot-OpenWebUI")
    try:
        await bot.polling()
    except Exception as e:
        logger.error("Bot polling failed with error: %s", e)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except (RuntimeError, asyncio.CancelledError) as e:
        logger.error("Application crashed: %s", e)
        exit(1)
