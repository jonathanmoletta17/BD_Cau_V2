import asyncio
import os
import sys
import json
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "agents" / "triage"))

try:
    from agents.triage.src.services.glpi_client import GLPIClient
    from agents.triage.src.config import settings
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

import logging

# Mute loggers
logging.basicConfig(level=logging.CRITICAL)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL)

async def analyze_printer_tickets():
    print("Initializing GLPI Client Analysis...", flush=True)
    client = GLPIClient()
    
    # We want to read from the WRITE target (usually Test in dev, but might be Prod depending on env)
    # OR we want to force read from PROD to get real history?
    # The user said "Utilize dados históricos disponíveis". In a real scenario, this is PROD.
    # However, 'GLPIClient' is configured to WRITE to 'target'.
    
    # Let's try to use the client's configured write_url/token first, assuming that's where we can query.
    # If we need PROD history specifically and we are in DEV pointing to TEST, this might return empty or fake data.
    # But adhering to "use available data".
    
    try:
        if not await client.init_session():
            print("Failed to init session.")
            return

        print(f"Connected to: {client.write_url}")
        
        # Determine strict search criteria or loose text search?
        # GLPI API search is complex. Let's list general tickets and filter locally for simplicity in this diagnostic tool.
        
        url = f"{client.write_url}/Ticket"
        headers = {
            "App-Token": client.write_app_token,
            "Session-Token": client.session_token
        }
        
        # Fetching a larger batch to filter
        params = {
            "range": "0-100",
            "order": "DESC",
            "sort": "date_creation",
            "is_deleted": 0
        }
        
        print("Fetching last 100 tickets...")
        response = await client.client.get(url, headers=headers, params=params)
        
        if response.status_code not in [200, 206]:
            print(f"Error fetching tickets: {response.status_code}")
            # print(response.text) # Too noisy
            return
            
        tickets = response.json()
        
        # Filter for Printer related
        keywords = ["impressora", "printer", "toner", "papel", "atolou", "mancha", "scanner"]
        printer_tickets = []
        
        for t in tickets:
            name = str(t.get("name", "")).lower()
            content = str(t.get("content", "")).lower()
            if any(k in name for k in keywords) or any(k in content for k in keywords):
                printer_tickets.append(t)
        
        output_lines = []
        output_lines.append(f"DEBUG: Fetched {len(tickets)} total tickets. Found {len(printer_tickets)} printer tickets.\n")
        output_lines.append(f"Found {len(printer_tickets)} related tickets.\n")
        
        for t in printer_tickets[:15]: # Analyze top 15
            output_lines.append("-" * 50)
            output_lines.append(f"ID: {t.get('id')} | Date: {t.get('date_creation')}")
            output_lines.append(f"Title: {t.get('name')}")
            content_clean = t.get('content', '')[:300].replace('\n', ' ')
            output_lines.append(f"Content (First 300 chars): {content_clean}")
            
            output_lines.append("\n[Evidência de Dados Estruturados?]")
            output_lines.append(f"  - Locations ID: {t.get('locations_id')}")
            output_lines.append(f"  - Items ID (Hardware Code): {t.get('items_id')}")
            output_lines.append(f"  - Category ID: {t.get('itilcategories_id')}")
            
            # Analyze content for patterns
            content_lower = t.get('content', '').lower()
            has_ip = "192." in content_lower or "10." in content_lower
            has_queue = "\\" in content_lower or "fila" in content_lower
            has_tag = "patrimonio" in content_lower or "etiqueta" in content_lower
            
            output_lines.append(f"  - Menção de IP (Texto): {has_ip}")
            output_lines.append(f"  - Menção de Fila (Texto): {has_queue}")
            output_lines.append(f"  - Menção de Patrimônio (Texto): {has_tag}")
            output_lines.append("-" * 50)

        report_path = os.path.join(str(project_root), "report_printers_utf8.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
            
        print(f"Analysis complete. Report written to: {report_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_printer_tickets())
