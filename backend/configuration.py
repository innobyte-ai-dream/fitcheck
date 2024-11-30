import os
from dotenv import load_dotenv

# Configuration
AZURE_OPEN_AI_API_KEY = os.environ.get("AZURE_OPEN_AI_API_KEY")
AZURE_OPEN_AI_URL = os.environ.get("AZURE_OPEN_AI_URL")
GPT35_AZURE_OPEN_AI_URL = os.environ.get("GPT35_AZURE_OPEN_AI_URL")
AZURE_REGION = os.getenv("AZURE_SERVICE_REGION", "eastus2")
