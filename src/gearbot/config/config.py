"""
Configuration module: loads environment variables and sets defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AI MODEL CONFIG
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4-fast")
# BROWSER CONFIG
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false")
NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))
TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "15000"))
# ENVIRONMENT CONFIG
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEVELOPMENT")
# LOGGING CONFIG
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
