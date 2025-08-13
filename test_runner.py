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