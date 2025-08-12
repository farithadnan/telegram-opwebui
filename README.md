# Telebot-OpenWebUI

A Telegram bot integrated with OpenWebUI for AI-powered conversations. This project serves as a bridge between Telegram users and an OpenWebUI-powered AI service, allowing users to interact with an AI language model through Telegram messaging.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
  - [Environment Configuration](#environment-configuration)
- [Running the Project](#running-the-project)
  - [Method 1: Using Docker Compose (Recommended)](#method-1-using-docker-compose-recommended)
  - [Method 2: Local Development with UV](#method-2-local-development-with-uv)
  - [Method 3: Using Dev Container (VS Code)](#method-3-using-dev-container-vs-code)
    - [Rebuilding Containers](#rebuilding-containers)
    - [Switching Between Environments](#switching-between-environments)
  - [Method 4: Using GitHub Container Registry Image](#method-4-using-github-container-registry-image)
- [Project Documentation](#project-documentation)

## Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Python 3.10 or higher** - Required for running the application
2. **uv** - Python package manager (install with `pip install uv`)
3. **Docker & Docker Compose** - For containerized deployment
4. **Visual Studio Code** (optional) - For dev container development
5. **OpenWebUI Instance** - Running instance with API access
6. **Telegram Bot Token** - From [@BotFather](https://t.me/BotFather) on Telegram

## Project Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd telebot-opwebui
   ```

2. Create the configuration directory and environment file, you can refer to the `config/.env.example` file for reference:

    ```bash
    touch config/.env
    ```

### Environment Configuration

Before running the project, you need to configure your environment variables in `config/.env`:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenWebUI Configuration
OPWEBUI_CHAT_ENDPOINT=http://localhost:3000/ollama/api/chat
OPWEBUI_JWT_TOKEN=your_openwebui_jwt_token_here
OPWEBUI_MODEL=llama3:8b
OPWEBUI_COLLECTION_ID=your_collection_id_here

# Custom Messages
WELCOME_MESSAGE=Welcome to the AI Telegram Bot! Send me any question and I'll answer it.
SYSTEM_PROMPT=You are a helpful AI assistant.
```

Make sure to replace the placeholder values with your actual configuration:

- `TELEGRAM_BOT_TOKEN`: Get this from @BotFather on Telegram
- `OPWEBUI_CHAT_ENDPOINT`: The chat endpoint of your OpenWebUI instance
- `OPWEBUI_JWT_TOKEN`: JWT token from your OpenWebUI instance
- `OPWEBUI_MODEL`: The model you want to use in OpenWebUI

## Running the Project

### Method 1: Using Docker Compose (Recommended)

This is the recommended approach for running the project as it ensures consistency across different environments:

```bash
docker-compose up -d
```

This command will:

- Build the Docker image
- Start the container with the proper environment configuration
- Mount the necessary volumes for code, logs, and configuration
- Run the application in detached mode

To view the logs:

```bash
docker-compose logs -f
```

To stop the container:

```bash
docker-compose down
```

### Method 2: Local Development with UV

For local development without containers:

1. Create a virtual environment using uv:

    ```bash
    uv venv
    ```

2. Activate the virtual environment:

    - On Windows (PowerShell):  
        ```powershell
            .venv\Scripts\Activate.ps1
        ```
    - On Windows (Command Prompt):
        ```cmd
        .venv\Scripts\activate.bat
        ```
    - On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3. Install dependencies:

    ```bash
    uv pip install -e .
    ```

4. Run the application:

    ```bash
    python main.py
    ```

### Method 3: Using Dev Container (VS Code)

If you prefer to develop in a containerized environment using VS Code Dev Containers:

1. Open the project in VS Code
2. When prompted, click "Reopen in Container" or:
    - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
    - Type "**Dev Containers: Reopen in Container**"
    - Select it and press Enter

The dev container will:

- Automatically build and start the container
- Install required extensions
- Set up the Python environment
- Mount the project directory for development

#### Rebuilding Containers
If you make changes to the Dockerfile, docker-compose.yml, or devcontainer.json, you'll need to rebuild the containers:

- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "**Dev Containers: Rebuild Container**"
- Select it and press Enter

This will rebuild the container with your changes.

#### Switching Between Environments

To switch back from the dev container to your local folder:

1. Look at the bottom-left corner of VS Code window where you'll see the container name
2. Click on it
3. Select "**Reopen Folder Locally**" from the options

This will switch you back to working on the project with your local environment instead of the container.


### Method 4: Using GitHub Container Registry Image

If you have GitHub Actions set up, a Docker image is automatically built and pushed to GitHub Container Registry (GHCR). You can run this image directly without cloning the entire repository.


#### Option 1: Using a local configuration file


1. Create a directory for your configuration:
   ```bash
   mkdir telebot-opwebui-config
   cd telebot-opwebui-config
   ```
2. Create a `.env` file with your configuration:

    ```bash
    # Create .env file with your settings
    cat > .env << EOF
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

    # OpenWebUI Configuration
    OPWEBUI_CHAT_ENDPOINT=http://localhost:3000/ollama/api/chat
    OPWEBUI_JWT_TOKEN=your_openwebui_jwt_token_here
    OPWEBUI_MODEL=llama3:8b
    OPWEBUI_COLLECTION_ID=your_collection_id_here

    # Custom Messages
    WELCOME_MESSAGE=Welcome to the AI Telegram Bot! Send me any question and I'll answer it.
    SYSTEM_PROMPT=You are a helpful AI assistant.
    EOF
    ```

3. Run the Docker container:

    ```bash
    docker run -d \
    --name telebot-opwebui \
    --network host \
    -v ./logs:/app/logs \
    --env-file ./.env \
    ghcr.io/your-github-username/your-repo-name:main
    ```

#### Option 2: Passing environment variables directly


Alternatively, you can pass environment variables directly:

```bash
docker run -d \
  --name telebot-opwebui \
  --network host \
  -v ./logs:/app/logs \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token \
  -e OPWEBUI_CHAT_ENDPOINT=http://localhost:3000/ollama/api/chat \
  -e OPWEBUI_JWT_TOKEN=your_openwebui_jwt_token \
  -e OPWEBUI_MODEL=llama3:8b \
  -e OPWEBUI_COLLECTION_ID=your_collection_id \
  -e WELCOME_MESSAGE="Welcome to the AI Telegram Bot! Send me any question and I'll answer it." \
  -e SYSTEM_PROMPT="You are a helpful AI assistant." \
  ghcr.io/your-github-username/your-repo-name:main
```

**Important:** When using the GitHub Container Registry image, make sure to:

1. Replace `your-github-username` and `your-repo-name` with your actual GitHub username and repository name
2. Ensure all required environment variables are provided either through the `--env-file` option or individual `-e` flags
3. You do not need to clone the repository to use the Docker image - just create your configuration locally.
4. The `-v ./logs:/app/logs` option will create a logs directory in your current folder to store application logs

---

## Project Documentation

For a detailed technical overview of the project, including:

- Core components and methods
- Libraries and dependencies
- Project structure
- Code explanations

Please refer to the [Project Documentation](/docs/project.md).