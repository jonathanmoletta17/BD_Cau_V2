import asyncio
import os
import sys
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.services.llm_service import LLMService
from src.services.classifier_service import ClassifierService
from src.services.glpi_client import GLPIClient
from src.models import ClassificationRequest

# Setup minimal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    id: int
    description: str
    expected_type: int  # 1=Incident, 2=Request
    expected_context: str # Partial match for category or title context
    requester_id: int
    entity_id: int

TEST_CASES = [
    TestCase(1, "O servidor de arquivos parou de responder e todo o setor financeiro está parado.", 1, "Servidor", 19, 0), # Critical Infra
    TestCase(2, "Minha impressora HP não está puxando papel da bandeja.", 1, "Impressora", 19, 0), # Hardware Incident
    TestCase(3, "Esqueci minha senha do GLPI e preciso resetar.", 2, "Acesso", 19, 0), # Access Request
    TestCase(4, "Preciso do Adobe Acrobat instalado no meu computador.", 2, "Software", 19, 0), # Software Request
    TestCase(5, "A internet do 3º andar está caindo toda hora.", 1, "Rede", 19, 0), # Network Incident
    TestCase(6, "Solicito um novo monitor para a estação de trabalho 04.", 2, "Periféricos", 19, 0), # Hardware Request
    TestCase(7, "Não consigo acessar a pasta compartilhada do RH.", 1, "Acesso", 19, 0), # Access Incident
    TestCase(8, "Meu Outlook não está baixando novos emails.", 1, "Email", 19, 0), # Software Incident
    TestCase(9, "O ar condicionado da sala de servidores pifou.", 1, "Infraestrutura", 19, 0), # Facilities? (Check category)
    TestCase(10, "Gostaria de saber como configuro minha assinatura de email.", 2, "Dúvida", 19, 0) # Knowledge Request
]

# Using User ID 19 (glpi default) and Entity 0 (Root) for testing to ensure safety if IDs differ in TEST env.
# Ideally we would use 141 (Jorge) but 19 is safer as generic 'glpi' user usually exists.

async def verify_batch():
    logger.info("🚀 Starting Batch Verification of 10 Tickets...")
    
    # Init Services
    llm = LLMService()
    classifier = ClassifierService(llm)
    glpi = GLPIClient()
    
    # Init Session
    if not await glpi.init_session():
        logger.error("❌ Failed to initialize GLPI Session. Aborting.")
        return

    report_lines = []
    report_lines.append("| ID | Description | Generated Title | Type | Urg | Imp | Req | Ent | Status |")
    report_lines.append("|---|---|---|---|---|---|---|---|---|")

    passed_count = 0

    for case in TEST_CASES:
        logger.info(f"Processing Case {case.id}: {case.description[:50]}...")
        
        # 1. Classify
        req = ClassificationRequest(title=case.description[:30], description=case.description)
        try:
            result = await classifier.classify(req)
        except Exception as e:
            logger.error(f"Classification failed for {case.id}: {e}")
            report_lines.append(f"| {case.id} | {case.description[:20]} | ERROR | - | - | - | - | - | ❌ Classify Error |")
            continue

        # 2. Validate Title Language (Basic Heuristic)
        title_ok = True
        if "Device Malfunction" in result.suggested_title or "Request" in result.suggested_title.split('] ')[-1]:
             # Simple check for English words in the description part
             pass 
             # We rely on visual check mostly, but let's log it.
        
        # 3. Create Ticket
        try:
            ticket_resp = await glpi.create_ticket(
                title=result.suggested_title,
                description=case.description,
                category_id=result.selected_category_id,
                ticket_type=result.ticket_type,
                urgency=result.urgency,
                impact=result.impact,
                requester_id=case.requester_id,
                entities_id=case.entity_id,
                ai_analysis=result.reasoning
            )
            ticket_id = ticket_resp.get('id')
        except Exception as e:
            logger.error(f"Ticket creation failed for {case.id}: {e}")
            report_lines.append(f"| {case.id} | {case.description[:20]} | {result.suggested_title} | {result.ticket_type} | {result.urgency} | {result.impact} | {case.requester_id} | {case.entity_id} | ❌ Create Error |")
            continue

        # 4. Fetch to Verify Persistence
        try:
            # Manual GET since GLPIClient doesn't expose get_ticket yet
            url = f"{glpi.write_url}/Ticket/{ticket_id}"
            headers = {"App-Token": glpi.write_app_token, "Session-Token": glpi.session_token}
            get_resp = await glpi.client.get(url, headers=headers)
            ticket_data = get_resp.json()
            
            # Verify Fields
            real_title = ticket_data.get('name')
            real_type = ticket_data.get('type')
            real_urgency = ticket_data.get('urgency')
            real_impact = ticket_data.get('impact')
            # Requester is tricky in API response, usually in _users_id_requester or separate link
            # GLPI API response for Ticket often has users_id_recipient
            real_recipient = ticket_data.get('users_id_recipient') 
            real_entity = ticket_data.get('entities_id')

            # Assertions
            checks = []
            if real_title == result.suggested_title: checks.append("Title✅")
            else: checks.append(f"Title❌({real_title})")
            
            if int(real_type) == result.ticket_type: checks.append("Type✅")
            else: checks.append(f"Type❌({real_type}!={result.ticket_type})")
            
            if int(real_entity) == case.entity_id: checks.append("Ent✅")
            else: checks.append(f"Ent❌({real_entity})")
            
            # Recipient validation (Requester)
            if int(real_recipient) == case.requester_id: checks.append("Req✅")
            else: checks.append(f"Req❌({real_recipient})")

            status = "✅" if all("✅" in c for c in checks) else "⚠️"
            if status == "✅": passed_count += 1
            
            report_lines.append(f"| {case.id} | {case.description[:20]}... | {real_title} | {real_type} | {real_urgency} | {real_impact} | {real_recipient} | {real_entity} | {status} {' '.join(checks)} |")

        except Exception as e:
            logger.error(f"Verification fetch failed for ticket {ticket_id}: {e}")
            report_lines.append(f"| {case.id} | {case.description[:20]} | {result.suggested_title} | - | - | - | - | - | ❌ Verify Error |")

    # Output Report
    print("\n\n" + "\n".join(report_lines))
    print(f"\nTotal Passed: {passed_count}/{len(TEST_CASES)}")
    
    # Save to file
    with open("batch_verification_results.md", "w", encoding="utf-8") as f:
        f.write("# Relatório de Verificação em Lote (10 Tickets)\n\n")
        f.write(f"**Data:** {os.popen('date /t').read().strip()}\n")
        f.write(f"**Total Sucesso:** {passed_count}/{len(TEST_CASES)}\n\n")
        f.write("\n".join(report_lines))

if __name__ == "__main__":
    asyncio.run(verify_batch())
