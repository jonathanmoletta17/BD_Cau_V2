#!/usr/bin/env python3
"""
Testes Reduzidos: 20 Casos Representativos
Timeout: 60s por request
"""

import sys
sys.path.insert(0, '/home/workbench/projects/BD_Cau_V2')

from exhaustive_tests import TODExhaustiveTester

# 20 casos selecionados estrategicamente
SELECTED_TEST_CASES = [
    # PRINTER_ISSUE (5 casos)
    {'description': '[P1] Impressora sem toner - completo',
     'message': 'impressora sem toner na sala 205, ramal 4221',
     'expected_intent': 'PRINTER_ISSUE', 'category': 'PRINTER_ISSUE', 'context': {}},
    
    {'description': '[P2] Impressora atolou - incompleto',
     'message': 'impressora atolou o papel',
     'expected_intent': 'PRINTER_ISSUE', 'category': 'PRINTER_ISSUE', 
     'context': {'location': 'sala 101', 'extension': '4121'}},
    
    {'description': '[P3] Impressora não imprime - MAIÚSCULAS',
     'message': 'IMPRESSORA NÃO IMPRIME',
     'expected_intent': 'PRINTER_ISSUE', 'category': 'PRINTER_ISSUE', 'context': {}},
    
    {'description': '[P4] Toner acabou',
     'message': 'toner acabou preciso trocar',
     'expected_intent': 'PRINTER_ISSUE', 'category': 'PRINTER_ISSUE', 'context': {}},
    
    {'description': '[P5] Impressora offline',
     'message': 'impressora aparece como offline',
     'expected_intent': 'PRINTER_ISSUE', 'category': 'PRINTER_ISSUE', 'context': {}},
    
    # NETWORK_ISSUE (5 casos)
    {'description': '[N1] Sem internet - completo',
     'message': 'estou sem internet aqui na sala 305, ramal 4001',
     'expected_intent': 'NETWORK_ISSUE', 'category': 'NETWORK_ISSUE', 'context': {}},
    
    {'description': '[N2] WiFi não conecta',
     'message': 'wifi não está conectando',
     'expected_intent': 'NETWORK_ISSUE', 'category': 'NETWORK_ISSUE', 'context': {}},
    
    {'description': '[N3] Rede lenta',
     'message': 'internet muito lenta não abre nada',
     'expected_intent': 'NETWORK_ISSUE', 'category': 'NETWORK_ISSUE', 'context': {}},
    
    {'description': '[N4] Cabo de rede quebrado',
     'message': 'cabo de rede não funciona',
     'expected_intent': 'NETWORK_ISSUE', 'category': 'NETWORK_ISSUE', 'context': {}},
    
    {'description': '[N5] WiFi oscilando',
     'message': 'wifi fica caindo toda hora',
     'expected_intent': 'NETWORK_ISSUE', 'category': 'NETWORK_ISSUE', 'context': {}},
    
    # CREATE_USER (3 casos) - testa loops e variações
    {'description': '[U1] Criar usuário novo estagiário',
     'message': 'criar usuario para novo estagiario',
     'expected_intent': 'CREATE_USER', 'category': 'CREATE_USER', 'context': {}},
    
    {'description': '[U2] Cadastrar servidor - formal',
     'message': 'preciso cadastrar um novo servidor no AD',
     'expected_intent': 'CREATE_USER', 'category': 'CREATE_USER', 'context': {}},
    
    {'description': '[U3] Novo usuário rede',
     'message': 'novo usuario para acesso a rede',
     'expected_intent': 'CREATE_USER', 'category': 'CREATE_USER', 'context': {}},
    
    # RESET_PASSWORD (3 casos)
    {'description': '[R1] Resetar senha - direto',
     'message': 'preciso resetar minha senha do sistema',
     'expected_intent': 'RESET_PASSWORD', 'category': 'RESET_PASSWORD', 'context': {}},
    
    {'description': '[R2] Esqueci senha',
     'message': 'esqueci a senha',
     'expected_intent': 'RESET_PASSWORD', 'category': 'RESET_PASSWORD', 'context': {}},
    
    {'description': '[R3] Senha bloqueada',
     'message': 'conta bloqueou por erro de senha',
     'expected_intent': 'RESET_PASSWORD', 'category': 'RESET_PASSWORD', 'context': {}},
    
    # EQUIPMENT_REQUEST (2 casos)
    {'description': '[E1] Solicitar mouse',
     'message': 'preciso de um mouse novo',
     'expected_intent': 'EQUIPMENT_REQUEST', 'category': 'EQUIPMENT_REQUEST', 'context': {}},
    
    {'description': '[E2] Notebook home office',
     'message': 'preciso pedir notebook para home office',
     'expected_intent': 'EQUIPMENT_REQUEST', 'category': 'EQUIPMENT_REQUEST', 'context': {}},
    
    # VPN_ACCESS (1 caso)
    {'description': '[V1] Acesso túnel VPN',
     'message': 'preciso de acesso ao tunel para trabalho remoto',
     'expected_intent': 'VPN_ACCESS', 'category': 'VPN_ACCESS', 'context': {}},
    
    # SOFTWARE_INSTALLATION (1 caso)
    {'description': '[S1] Instalar Office',
     'message': 'preciso instalar o pacote office',
     'expected_intent': 'SOFTWARE_INSTALLATION', 'category': 'SOFTWARE_INSTALLATION', 'context': {}},
]

if __name__ == '__main__':
    print("🚀 Testes Reduzidos: 20 Casos Selecionados")
    print(f"⏱️  Timeout: 60s por request")
    print(f"📊 Tempo estimado: ~10-15 minutos\n")
    
    # Modificar timeout no teste
    tester = TODExhaustiveTester()
    
    # Sobrescrever send_message com timeout maior
    original_send = tester.send_message
    def send_with_long_timeout(message, conversation_id=None):
        import requests
        try:
            payload = {'message': message}
            if conversation_id:
                payload['conversationId'] = conversation_id
            
            response = requests.post(
                tester.api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # 60 segundos
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                'error': str(e),
                'response': '',
                'state': {'isComplete': False, 'missingSlots': []}
            }
    
    tester.send_message = send_with_long_timeout
    
    # Executar testes
    tester.test_batch(SELECTED_TEST_CASES, output_dir='./test_results_reduced')
