import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "test")

GLPI_TEST_URL = os.getenv("GLPI_TEST_URL", "http://10.72.16.202/atual/apirest.php")
GLPI_TEST_USER_TOKEN = os.getenv("GLPI_TEST_USER_TOKEN", "")
GLPI_TEST_APP_TOKEN = os.getenv("GLPI_TEST_APP_TOKEN", "")

GLPI_PROD_URL = os.getenv("GLPI_PROD_URL", "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php")
GLPI_PROD_USER_TOKEN = os.getenv("GLPI_PROD_USER_TOKEN", "")
GLPI_PROD_APP_TOKEN = os.getenv("GLPI_PROD_APP_TOKEN", "")

HTTPS_ONLY = False
CA_BUNDLE_PATH = os.getenv("CA_BUNDLE_PATH", "")

CSV_PATH = os.getenv("GLPI_CSV_PATH", r"c:\\Users\\jonathan-moletta\\Projetos_Locais\\BD_Cau_V2\\glpi-dtic-agent-classificator\\glpi.csv")

DEVICE = os.getenv("AGENT_DEVICE", "cpu")
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "stub")
EMB_BATCH_SIZE = int(os.getenv("EMB_BATCH_SIZE", "32"))

AUTO_CONFIRM_THRESHOLD = float(os.getenv("AUTO_CONFIRM_THRESHOLD", "0.90"))
KEEP_CURRENT_THRESHOLD = float(os.getenv("KEEP_CURRENT_THRESHOLD", "0.90"))
MARGINAL_DIFF = float(os.getenv("MARGINAL_DIFF", "0.05"))
DISCREPANCY_ACT = float(os.getenv("DISCREPANCY_ACT", "0.10"))
SUBCATEGORY_MARGIN = float(os.getenv("SUBCATEGORY_MARGIN", "0.05"))
SUBCATEGORY_MIN = float(os.getenv("SUBCATEGORY_MIN", "0.80"))

SANDBOX = os.getenv("SANDBOX", "true").lower() == "true"

LOG_DIR = os.getenv("LOG_DIR", "logs")
REPORT_DIR = os.getenv("REPORT_DIR", "reports")
ROLLBACK_PATH = os.getenv("ROLLBACK_PATH", "rollback.json")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
