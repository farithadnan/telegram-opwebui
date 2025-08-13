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
- [Testing](#testing)
  - [Test Suite Structure](#test-suite-structure)
  - [Test Runner](#test-runner)
  - [Running Tests](#running-tests)
- [Libraries and Dependencies](#libraries-and-dependencies)
  - [Core Libraries](#core-libraries)
  - [Development and Deployment Tools](#development-and-deployment-tools)
- [Project Configuration and Deployment](#project-configuration-and-deployment)
    - [Docker Configuration](#docker-configuration)
    - [Python Project Configuration](#python-project-configuration)
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
- `OPWEBUI_MODEL`: The specific model to use with OpenWebUI whether using a local model or a remote model or a custom model you created with OpenWebUI
- `OPWEBUI_COLLECTION_ID`: The collection ID for context-specific information or knowledge you created in OpenWebUI
- `WELCOME_MESSAGE`: Customizable welcome message for new users

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
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Unexpected error processing message from user %s after %.2fs: %s", 
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
```

The main function starts the bot using `asyncio.run(bot.polling())` which begins polling Telegram for new messages. It includes proper exception handling for graceful shutdown.

---
## Testing

The project includes a comprehensive test suite to ensure code quality and reliability.

### Test Suite Structure

The tests are organized in the `tests/` directory with the following structure:

```markdown
tests/
├── test_env_loading.py         # Tests for environment variable loading
├── test_llm_processing.py      # Tests for LLM processing functions
└── test_message_handlers.py    # Tests for Telegram message handlers
```

1. `test_env_loading.py`: Tests environment variable loading and validation, ensuring the application properly handles missing or invalid configuration.
2. `test_llm_processing.py`: Tests the LLM processing functionality with various scenarios:
    - Successful responses
    - Different response formats
    - HTTP errors
    - Timeout errors
    - Connection errors
    - Invalid JSON responses
    - Unexpected response formats
3. `test_message_handlers.py`: Tests the Telegram message handlers:
    - Welcome message handler
    - Regular message handler
    - Error handling in message processing


### Test Runner

A dedicated test runner script (`test_runner.py`) is provided to simplify test execution:

```python
#!/usr/bin/env python3
"""Test runner script for local testing."""

import subprocess
import sys
import os


def run_tests():
    """Run all tests with pytest."""
    try:
        # Use uv to install all dependencies
        subprocess.run([
            "uv", "pip", "install", 
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.1",
            "requests-mock>=1.11.0",
            "python-dotenv",
            "pytelegrambotapi"
        ], check=True)
        
        # Run tests using the virtual environment's Python
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
        result = subprocess.run([venv_python, "-m", "pytest", "tests/", "-v"])
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        return False
    except FileNotFoundError:
        # Fallback to using python from PATH
        try:
            result = subprocess.run(["python", "-m", "pytest", "tests/", "-v"])
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error running tests: {e}")
            return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

This script:

1. Installs all necessary test dependencies using `uv`
2. Runs the tests using pytest
3. Provides proper error handling and exit codes


#### Running Tests

Tests can be executed in multiple ways:

1. Using the test runner script:

```bash
python test_runner.py
```

2. Directly with pytest (if dependencies are already installed):

```bash
python -m pytest tests/ -v
```

All tests should pass to ensure the application functions correctly.

---

## Libraries and Dependencies

### Core Libraries
1. **pyTelegramBotAPI**: An asynchronous Python library for interacting with Telegram's Bot API. It provides:
    - Message handling decorators
    - Methods for sending messages and chat actions
    - Support for both polling and webhook modes
2. **python-dotenv**: A library for loading environment variables from .env files, making configuration management easier.
3. **requests**: A popular HTTP library for making API requests to the OpenWebUI endpoint.
4. **asyncio**: Python's built-in library for writing asynchronous code, essential for handling multiple Telegram conversations concurrently.
5. **logging**: Python's standard logging module for tracking application behavior and debugging.

### Development and Deployment Tools

1. **uv**: A fast Python package installer and resolver used in the Dockerfile for dependency installation.
2. **Docker**: Containerization platform used for deployment consistency.
3. **docker-compose**: Tool for defining and running multi-container Docker applications.


## Project Configuration and Deployment

### Docker Configuration

The project includes Docker support for easy deployment and consistent environments across different systems.

#### Dockerfile
The `Dockerfile` defines the container image for the application:
- Uses Python 3.11 as the base image
- Creates a dedicated user for running the application
- Uses `uv` as the package manager for faster dependency installation
- Sets up proper directory structure and permissions
- Exposes port 8080 for potential web UI (if implemented)
- Configures the container to run the main application

#### Docker Compose
The `docker-compose.yml` file provides an easy way to run the application with proper configuration:
- Uses the locally built image
- Sets up proper volume mounts for logs and configuration
- Uses network_mode: "host" for simplified networking
- Loads environment variables from config/.env file

#### Dev Container Configuration
The `.devcontainer/devcontainer.json` file enables development in a containerized environment:
- Uses the same base image as the production Dockerfile
- Automatically installs development tools like uv
- Sets up proper user permissions
- Configures VS Code extensions for Python development
- Mounts the project directory for live editing

### Python Project Configuration

#### pyproject.toml

The pyproject.toml file contains project metadata and configuration:
- Project name, version, and description
- Python version requirement (>=3.11)
- Dependencies (pyTelegramBotAPI, python-dotenv, requests)
- Optional test dependencies for development
- pytest configuration for running tests
- Project structure definitions

#### Configuration Files

- config/.env: Contains environment variables required for the application
- logs/: Directory for application logs (git-ignored)

## Project Structure

```markdown
telebot-opwebui/
├── .devcontainer/
│   └── devcontainer.json     # VS Code dev container configuration
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
├── main.py                   # Main application code
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Project documentation
├── docs/                     # Detailed documentation
│   └── project.md            # This document
├── config/                   # Configuration directory (git-ignored)
│   └── .env                  # Environment variables
├── logs/                     # Log directory (git-ignored)
├── tests/                    # Test suite
│   ├── test_env_loading.py
│   ├── test_llm_processing.py
│   └── test_message_handlers.py
├── test_runner.py            # Test execution script
└── .github/                  # GitHub Actions workflows
    └── workflows/
        └── ci-cd.yml
```
---

## Setup Guide

For instructions on how to set up and run this project, please refer to the [README.md](../README.md).

