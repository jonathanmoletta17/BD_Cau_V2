"""
Test GLPI_SIS API Credentials and Connectivity
Purpose: Validate authentication, permissions, and response times
"""
import os
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# GLPI SIS Credentials
GLPI_SIS_URL = os.getenv('GLPI_SIS_URL')
GLPI_SIS_APP_TOKEN = os.getenv('GLPI_SIS_APP_TOKEN')
GLPI_SIS_USER_TOKEN = os.getenv('GLPI_SIS_USER_TOKEN')

def test_glpi_sis_connection():
    """Test GLPI SIS API connection and authentication."""
    
    print("=" * 60)
    print("GLPI SIS API - TESTE DE CONECTIVIDADE E CREDENCIAIS")
    print("=" * 60)
    print(f"\n[INFO] URL: {GLPI_SIS_URL}")
    print(f"[INFO] Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': GLPI_SIS_APP_TOKEN,
        'Authorization': f'user_token {GLPI_SIS_USER_TOKEN}'
    }
    
    results = {
        'authentication': False,
        'permissions': {},
        'response_times': {},
        'errors': []
    }
    
    # Test 1: Init Session (Authentication)
    print("[1/5] Testando Autenticação...")
    try:
        start = time.time()
        response = requests.get(
            f"{GLPI_SIS_URL}/initSession",
            headers=headers,
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            session_token = response.json().get('session_token')
            print(f"  ✓ Autenticação bem-sucedida (200 OK)")
            print(f"  ✓ Session Token recebido: {session_token[:20]}...")
            print(f"  ✓ Tempo de resposta: {elapsed:.2f}s")
            results['authentication'] = True
            results['response_times']['authentication'] = elapsed
            results['session_token'] = session_token
            
            # Update headers with session token
            headers['Session-Token'] = session_token
        else:
            print(f"  ✗ Falha na autenticação ({response.status_code})")
            print(f"  ✗ Resposta: {response.text}")
            results['errors'].append({
                'test': 'authentication',
                'status': response.status_code,
                'message': response.text
            })
            return results
            
    except Exception as e:
        print(f"  ✗ Erro na autenticação: {str(e)}")
        results['errors'].append({
            'test': 'authentication',
            'error': str(e)
        })
        return results
    
    # Test 2: Get Entities
    print("\n[2/5] Testando permissões - Entidades...")
    try:
        start = time.time()
        response = requests.get(
            f"{GLPI_SIS_URL}/Entity",
            headers=headers,
            params={'range': '0-4'},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            entities = response.json()
            print(f"  ✓ Acesso a Entidades OK (200)")
            print(f"  ✓ Entidades retornadas: {len(entities)}")
            print(f"  ✓ Tempo de resposta: {elapsed:.2f}s")
            results['permissions']['entities'] = True
            results['response_times']['entities'] = elapsed
            
            if entities:
                print(f"  ✓ Exemplo: {entities[0].get('name', 'N/A')}")
        else:
            print(f"  ✗ Falha ao acessar Entidades ({response.status_code})")
            results['permissions']['entities'] = False
            
    except Exception as e:
        print(f"  ✗ Erro ao acessar Entidades: {str(e)}")
        results['permissions']['entities'] = False
    
    # Test 3: Get Tickets
    print("\n[3/5] Testando permissões - Tickets...")
    try:
        start = time.time()
        response = requests.get(
            f"{GLPI_SIS_URL}/Ticket",
            headers=headers,
            params={'range': '0-4'},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"  ✓ Acesso a Tickets OK (200)")
            print(f"  ✓ Tickets retornados: {len(tickets)}")
            print(f"  ✓ Tempo de resposta: {elapsed:.2f}s")
            results['permissions']['tickets'] = True
            results['response_times']['tickets'] = elapsed
            
            if tickets:
                ticket = tickets[0]
                print(f"  ✓ Exemplo Ticket ID: {ticket.get('id')}")
                print(f"  ✓ Status: {ticket.get('status')}")
        else:
            print(f"  ✗ Falha ao acessar Tickets ({response.status_code})")
            results['permissions']['tickets'] = False
            
    except Exception as e:
        print(f"  ✗ Erro ao acessar Tickets: {str(e)}")
        results['permissions']['tickets'] = False
    
    # Test 4: Get Users
    print("\n[4/5] Testando permissões - Usuários...")
    try:
        start = time.time()
        response = requests.get(
            f"{GLPI_SIS_URL}/User",
            headers=headers,
            params={'range': '0-4'},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            users = response.json()
            print(f"  ✓ Acesso a Usuários OK (200)")
            print(f"  ✓ Usuários retornados: {len(users)}")
            print(f"  ✓ Tempo de resposta: {elapsed:.2f}s")
            results['permissions']['users'] = True
            results['response_times']['users'] = elapsed
        else:
            print(f"  ✗ Falha ao acessar Usuários ({response.status_code})")
            results['permissions']['users'] = False
            
    except Exception as e:
        print(f"  ✗ Erro ao acessar Usuários: {str(e)}")
        results['permissions']['users'] = False
    
    # Test 5: Kill Session
    print("\n[5/5] Encerrando sessão...")
    try:
        response = requests.get(
            f"{GLPI_SIS_URL}/killSession",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ Sessão encerrada com sucesso")
        else:
            print(f"  ! Aviso: Falha ao encerrar sessão ({response.status_code})")
            
    except Exception as e:
        print(f"  ! Aviso: Erro ao encerrar sessão: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"\nAutenticação: {'✓ OK' if results['authentication'] else '✗ FALHOU'}")
    
    print("\nPermissões:")
    for resource, status in results['permissions'].items():
        print(f"  - {resource.capitalize()}: {'✓ OK' if status else '✗ SEM ACESSO'}")
    
    if results['response_times']:
        print("\nTempo de Resposta Médio:")
        avg_time = sum(results['response_times'].values()) / len(results['response_times'])
        print(f"  {avg_time:.2f}s")
        print("\nDetalhamento:")
        for test, elapsed in results['response_times'].items():
            print(f"  - {test}: {elapsed:.2f}s")
    
    if results['errors']:
        print("\nErros Encontrados:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    
    return results

if __name__ == "__main__":
    test_glpi_sis_connection()
