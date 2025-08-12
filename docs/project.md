# Telebot-OpenWebUI Project Deep Dive

Telebot-OpenWebUI is a Python-based project that integrates a Telegram bot with the OpenWebUI LLM (Large Language Model) API. This integration allows users to interact with an AI language model through Telegram messaging, providing a convenient interface for AI-powered conversations.

## Table of Contents

- [Project Overview](#project-overview)
- [Core Components and Methods](#core-components-and-methods)
  - [Main Application (main.py)](#main-application-mainpy)
    - [Initialization and Configuration](#initialization-and-configuration)
    - [Environment Variables](#environment-variables)
    - [Bot Command Handlers](#bot-command-handlers)
    - [LLM Processing Function](#llm-processing-function)
    - [Application Entry Point](#application-entry-point)
- [Libraries and Dependencies](#libraries-and-dependencies)
  - [Core Libraries](#core-libraries)
  - [Development and Deployment Tools](#development-and-deployment-tools)
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)


## Project Overview

The project serves as a bridge between Telegram users and an OpenWebUI-powered AI service. It receives messages from Telegram users, forwards them to an OpenWebUI instance for processing, and returns the AI-generated responses back to the users via Telegram.

## Core Components and Methods

### Main Application (main.py)

The main application file contains the core functionality of the project:

#### Initialization and Configuration

The application starts by setting up logging and loading environment variables:

```python
import os
import json
import time
import asyncio
import logging

from pathlib import Path

import requests
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
```

- Uses Python's logging module to log events to both file (logs/telebot-opwebui.log) and console
- Loads environment variables from config/.env using python-dotenv
- Creates an instance of AsyncTeleBot using the provided Telegram bot token


#### Environment Variables

The application depends on several environment variables:

- `TELEGRAM_BOT_TOKEN`: The token for authenticating with Telegram's Bot API
- `OPWEBUI_CHAT_ENDPOINT`: The endpoint URL for the OpenWebUI chat API
- `OPWEBUI_JWT_TOKEN`: JWT token for authenticating with the OpenWebUI API
- `OPWEBUI_MODEL`: The specific model to use with OpenWebUI
- `OPWEBUI_COLLECTION_ID`: The collection ID for context-specific information
- `WELCOME_MESSAGE`: Customizable welcome message for new users
- `SYSTEM_PROMPT`: System prompt that guides the AI's behavior

#### Bot Command Handlers


```python
# Welcome handler
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    """Send a welcome message to the user"""
    logger.info(
        "User %s started conversation. Chat ID: %s",
        message.from_user.id,
        message.chat.id
    )
    await bot.reply_to(message, WELCOME_MESSAGE)
```
This handler responds to /start and /help commands with a customizable welcome message. It logs the user ID and chat ID for tracking purposes.

---

```python
# Message handler
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
```

This handler processes all text messages (except commands) as queries to be sent to the LLM. It:

1. Extracts user information and message content
2. Logs the received message
3. Shows "typing" indicator to the Telegram user
4. Processes the message with the LLM via process_with_llm function
5. Sends the response back to the user
6. Handles exceptions gracefully with error messages

---

#### LLM Processing Function

```python
# LLM Processing Function
async def process_with_llm(query: str, user_id: int = None, chat_id: int = None) -> str:
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
        # ... processing continues
```

The process_with_llm function is responsible for communicating with the OpenWebUI API:

1. Constructs appropriate headers with JWT authentication
2. Creates a JSON payload with:
    - Model to use
    - Message history (system prompt and user query)
    - Collection context (if specified)
3. Makes an HTTP POST request to the OpenWebUI chat endpoint
4. Implements comprehensive error handling for various failure scenarios:
    - Connection errors
    - Timeouts
    - HTTP errors
    - Invalid JSON responses
    - General request exceptions

The function extracts the response content from the API's JSON response, specifically looking for the message content in the expected format.

---

#### Application Entry point

```python
# Application Entry point
def main():
    """
    Main entry point for the application.
    """
    logger.info("Starting Telebot-OpenWebUI")
    asyncio.run(bot.polling())

if __name__ == "__main__":
    main()
```

The main function starts the bot using asyncio.run(bot.polling()) which begins polling Telegram for new messages.

---

### Libraries and Dependencies

#### Core Libraries
1. **pyTelegramBotAPI**: An asynchronous Python library for interacting with Telegram's Bot API. It provides:
    - Message handling decorators
    - Methods for sending messages and chat actions
    - Support for both polling and webhook modes
2. **python-dotenv**: A library for loading environment variables from .env files, making configuration management easier.
3. **requests**: A popular HTTP library for making API requests to the OpenWebUI endpoint.
4. **asyncio**: Python's built-in library for writing asynchronous code, essential for handling multiple Telegram conversations concurrently.
5. **logging**: Python's standard logging module for tracking application behavior and debugging.

#### Development and Deployment Tools

1. **uv**: A fast Python package installer and resolver used in the Dockerfile for dependency installation.
2. **Docker**: Containerization platform used for deployment consistency.
3. **docker-compose**: Tool for defining and running multi-container Docker applications.

### Project Structure

```markdown
telebot-opwebui/
├── .devcontainer/
│   └── devcontainer.json     # VS Code dev container configuration
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
├── main.py                   # Main application code
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Project documentation
├── config/                   # Configuration directory (git-ignored)
│   └── .env                  # Environment variables
└── logs/                     # Log directory (git-ignored)
```
---

## Setup Guide

For instructions on how to set up and run this project, please refer to the [README.md](../README.md).

