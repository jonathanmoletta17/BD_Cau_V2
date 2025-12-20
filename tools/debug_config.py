import sys
from pathlib import Path
import os

# Add path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "agents" / "triage"))

print(f"CWD: {os.getcwd()}")
print(f"Env file exists at CWD/.env? {os.path.exists('.env')}")

from dotenv import load_dotenv
load_dotenv()
print(f"GLPI_API_URL (env): {os.getenv('GLPI_API_URL')}")
print(f"GLPI_PROD_URL (env): {os.getenv('GLPI_PROD_URL')}")

from src.config import settings
print(f"Settings GLPI_API_URL: {settings.GLPI_API_URL}")
print(f"Settings GLPI_PROD_URL: {settings.GLPI_PROD_URL}")
print(f"Settings Dump: {settings.model_dump()}")
