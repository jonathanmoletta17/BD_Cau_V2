import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.config import ENVIRONMENT

def verify_latest():
    client = GlpiClient(environment=ENVIRONMENT)
    client.init_session()
    
    # Fetch 1 ticket, sort DESC by ID
    tickets = client.search_items("Ticket", {"is_deleted": "0", "sort": "id", "order": "DESC", "range": "0-1"})
    
    if not tickets:
        print("No tickets found.")
        return

    t = tickets[0]
    print(f"ID: {t['id']}")
    print(f"Title: {t['name']}")
    print(f"Urgency: {t.get('urgency')} (1=Muito Baixa, 2=Baixa, 3=Média, 4=Alta, 5=Muito Alta)")
    print(f"Impact: {t.get('impact')} (1=Muito Baixo, 2=Baixo, 3=Médio, 4=Alto, 5=Muito Alto)")
    print(f"Category ID: {t.get('itilcategories_id')}")
    
    cat_name = client.get_category_name(t.get('itilcategories_id'))
    print(f"Category Name (GLPI): {cat_name}")
    
    print("-" * 20)
    print("Content Preview (Description):")
    # Print first 500 chars to show the embedded JSON
    print(t['content'][:500] + "...")

if __name__ == "__main__":
    verify_latest()
