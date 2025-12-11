import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Proxy Bypass
os.environ["NO_PROXY"] = "localhost,127.0.0.1,10.72.16.202"

from glpi_agent.glpi_client import GlpiClient

# Initialize Client
client = GlpiClient()
client.init_session()



email = "joao-dias@casacivil.rs.gov.br"
print(f"Searching for email using SEARCH API (Criteria 5): {email}")

key_email = "5" # Standard Email field ID in GLPI

# Construct URL manually to bypass client's item list logic
# /search/User?criteria[0][field]=5&criteria[0][searchtype]=contains&criteria[0][value]=...&forcedisplay[0]=2
import urllib.parse
encoded_email = urllib.parse.quote(email)

# Using 'contains' to be safer, or 'equals' if precise. 
# Also adding forcedisplay[0]=2 to get the ID.
query = f"/search/User?criteria[0][field]={key_email}&criteria[0][searchtype]=contains&criteria[0][value]={encoded_email}&forcedisplay[0]=2"

cfg = client._creds()
url = cfg["url"].strip("/") + query

print(f"URL: {url}")
try:
    resp = client._get(url)
    print(json.dumps(resp, indent=2))
except Exception as e:
    print(f"Error: {e}")



