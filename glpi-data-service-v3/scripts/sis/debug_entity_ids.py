"""
Debug: Check entity IDs in SIS API
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config
from src.core.glpi_client import GLPIClient

with GLPIClient(
    config.GLPI_SIS_URL,
    config.GLPI_SIS_APP_TOKEN,
    config.GLPI_SIS_USER_TOKEN
) as client:
    
    # Get first 20 tickets
    tickets = client.make_request('Ticket', {'range': '0-19'})
    
    print(f"\nTotal tickets fetched: {len(tickets)}\n")
    
    # Count by entity
    entities_count = {}
    for tkt in tickets:
        ent_id = tkt.get('entities_id')
        entities_count[ent_id] = entities_count.get(ent_id, 0) + 1
    
    print("Tickets by entity_id:")
    for ent_id, count in sorted(entities_count.items()):
        print(f"  Entity {ent_id}: {count} tickets")
    
    # Show sample
    print(f"\nSample tickets:")
    for i, tkt in enumerate(tickets[:5]):
        print(f"  {i+1}. ID={tkt.get('id')}, Entity={tkt.get('entities_id')}, Name={tkt.get('name', '')[:40]}")
