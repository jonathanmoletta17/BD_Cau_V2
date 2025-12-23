#!/usr/bin/env python3
"""
Framework de Testes Exaustivos - Agente TOD com Dados Reais GLPI

Objetivo: Testar 200+ cenários reais do GLPI
Autor: Sistema TOD
Data: 22/12/2025
"""

import json
import requests
import time
import csv
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class Colors:
    """ANSI colors para output formatado"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TODExhaustiveTester:
    """Framework de testes exaustivos para agente TOD"""
    
    def __init__(self, api_url: str = "http://localhost:4000/chat"):
        self.api_url = api_url
        self.results = []
        self.start_time = datetime.now()
        self.test_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        
    def send_message(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """Envia mensagem para API do agente"""
        try:
            payload = {'message': message}
            if conversation_id:
                payload['conversationId'] = conversation_id
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                'error': str(e),
                'response': '',
                'state': {'isComplete': False, 'missingSlots': []}
            }
    
    def mock_slot_value(self, slot: str, ticket_context: Dict) -> str:
        """Gera valor mockado realista para slot"""
        
        # Valores baseados em dados reais comuns
        mock_values = {
            'location': [
                'sala 205', 'sala 101', 'sala 305', 'RH térreo',
                'Casa Amarela sala 201', 'DTIC 3º andar',
                'Secretaria', 'Gabinete'
            ],
            'extension': [
                '4221', '4121', '4001', '4321', '4444',
                'ramal 3000', '2500'
            ],
            'userName': [
                'João Silva', 'Maria Santos', 'Pedro Oliveira',
                'Ana Costa', 'Carlos Ferreira'
            ],
            'organization': [
                'Casa Civil', 'SECOM', 'Casa Militar',
                'Secretaria da Educação', 'PROCERGS'
            ],
            'sector': [
                'DTIC', 'RH', 'Financeiro', 'Compras',
                'Patrimônio', 'TI'
            ],
            'jobTitle': [
                'Técnico de TI', 'Analista', 'Coordenador',
                'Estagiário', 'Gerente', 'Diretor'
            ],
            'cpf': ['12345678900', '98765432100'],
        }
        
        # Retornar valor do contexto se disponível, senão mock
        if slot in ticket_context:
            return ticket_context[slot]
        
        import random
        return random.choice(mock_values.get(slot, ['informação padrão']))
    
    def test_conversation(
        self, 
        initial_message: str, 
        ticket_context: Dict,
        max_turns: int = 15
    ) -> Dict:
        """
        Testa uma conversa completa
        
        Returns:
            Dict com métricas detalhadas da conversa
        """
        start_time = time.time()
        conversation_id = None
        turns = []
        loops_detected = {}
        
        try:
            # Turno 1: Mensagem inicial
            response = self.send_message(initial_message)
            conversation_id = response.get('conversationId')
            
            turns.append({
                'turn': 1,
                'user': initial_message,
                'bot': response.get('response', ''),
                'state': response.get('state', {}),
                'action': response.get('action', {}),
                'timestamp': time.time() - start_time
            })
            
            # Loop de conversa
            turn = 2
            last_slot = None
            slot_attempts = {}
            
            while turn <= max_turns:
                state = turns[-1]['state']
                
                # Verificar se completo
                if state.get('isComplete'):
                    # Confirmar
                    response = self.send_message("sim", conversation_id)
                    turns.append({
                        'turn': turn,
                        'user': 'sim',
                        'bot': response.get('response', ''),
                        'state': response.get('state', {}),
                        'action': response.get('action', {}),
                        'timestamp': time.time() - start_time
                    })
                    
                    # Sucesso se ticket criado
                    success = bool(response.get('ticketId'))
                    break
                
                # Verificar slots faltantes
                missing = state.get('missingSlots', [])
                if not missing:
                    break
                
                next_slot = missing[0]
                
                # Detectar loops
                if next_slot == last_slot:
                    slot_attempts[next_slot] = slot_attempts.get(next_slot, 0) + 1
                    
                    if slot_attempts[next_slot] > 5:
                        loops_detected[next_slot] = slot_attempts[next_slot]
                        break  # Abortar se loop infinito
                else:
                    slot_attempts[next_slot] = 1
                
                last_slot = next_slot
                
                # Fornecer valor para slot
                value = self.mock_slot_value(next_slot, ticket_context)
                response = self.send_message(value, conversation_id)
                
                turns.append({
                    'turn': turn,
                    'user': value,
                    'slot_filled': next_slot,
                    'bot': response.get('response', ''),
                    'state': response.get('state', {}),
                    'action': response.get('action', {}),
                    'timestamp': time.time() - start_time
                })
                
                turn += 1
            else:
                # Max turns atingido
                success = False
            
            duration = time.time() - start_time
            
            # Calcular métricas
            intent = turns[0]['state'].get('intent', 'UNKNOWN')
            total_turns = len(turns)
            slots_filled = []
            
            for turn_data in turns:
                if 'slot_filled' in turn_data:
                    slots_filled.append(turn_data['slot_filled'])
            
            return {
                'conversation_id': conversation_id,
                'initial_message': initial_message[:100],
                'intent_detected': intent,
                'total_turns': total_turns,
                'success': success if 'success' in locals() else False,
                'ticket_created': success if 'success' in locals() else False,
                'duration_seconds': round(duration, 2),
                'slots_filled': slots_filled,
                'loops_detected': loops_detected,
                'has_loops': len(loops_detected) > 0,
                'turns_detail': turns,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'initial_message': initial_message[:100],
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_batch(self, test_cases: List[Dict], output_dir: str = './test_results'):
        """Executa batch de testes"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        print(f"\n{Colors.BOLD}🧪 TESTES EXAUSTIVOS - Agente TOD{Colors.RESET}")
        print(f"{'='*70}")
        print(f"📊 Total de testes: {len(test_cases)}")
        print(f"🎯 API: {self.api_url}")
        print(f"📁 Output: {output_dir}")
        print(f"{'='*70}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{Colors.BLUE}[{i}/{len(test_cases)}]{Colors.RESET} Testando: {test_case['description'][:60]}...", end=' ')
            
            result = self.test_conversation(
                test_case['message'],
                test_case.get('context', {})
            )
            
            # Adicionar metadata
            result['test_id'] = i
            result['expected_intent'] = test_case.get('expected_intent')
            result['category'] = test_case.get('category')
            result['description'] = test_case.get('description')
            
            self.results.append(result)
            
            # Status visual
            if result['success']:
                print(f"{Colors.GREEN}✅ OK{Colors.RESET} ({result['total_turns']} turnos, {result['duration_seconds']}s)")
            elif result.get('has_loops'):
                print(f"{Colors.YELLOW}⚠️  LOOP{Colors.RESET} (slot: {list(result['loops_detected'].keys())})")
            else:
                print(f"{Colors.RED}❌ FALHA{Colors.RESET}")
            
            # Pausa breve
            time.sleep(0.3)
        
        # Gerar relatórios
        self.save_results(output_dir)
        self.generate_reports(output_dir)
    
    def save_results(self, output_dir: str):
        """Salva resultados brutos em JSON"""
        filename = f"{output_dir}/results_{self.test_id}.json"
        
        data = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'api_url': self.api_url,
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos: {filename}")
    
    def generate_reports(self, output_dir: str):
        """Gera relatórios analíticos"""
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success'))
        with_loops = sum(1 for r in self.results if r.get('has_loops'))
        
        # Taxa de sucesso
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Média de turnos
        avg_turns = sum(r.get('total_turns', 0) for r in self.results) / total if total > 0 else 0
        
        # Intents
        intents = {}
        for r in self.results:
            intent = r.get('intent_detected', 'UNKNOWN')
            intents[intent] = intents.get(intent, 0) + 1
        
        # Duração média
        avg_duration = sum(r.get('duration_seconds', 0) for r in self.results) / total if total > 0 else 0
        
        # Gerar relatório MD
        report_md = f"""# Relatório de Testes Exaustivos

**Test ID:** {self.test_id}  
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**API:** {self.api_url}

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de testes** | {total} |
| **Sucessos** | {successful} ({success_rate:.1f}%) |
| **Falhas** | {total - successful} ({100-success_rate:.1f}%) |
| **Com loops** | {with_loops} |
| **Turnos médios** | {avg_turns:.2f} |
| **Duração média** | {avg_duration:.2f}s |

---

## 🎯 Intents Detectados

| Intent | Quantidade | Percentual |
|--------|-----------|------------|
"""
        
        for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100)
            report_md += f"| {intent} | {count} | {percentage:.1f}% |\n"
        
        report_md += f"""
---

## ⚠️  Top Problemas

"""
        
        # Listar casos com loop
        loop_cases = [r for r in self.results if r.get('has_loops')]
        if loop_cases:
            report_md += "### Loops Detectados\n\n"
            for r in loop_cases[:10]:
                report_md += f"- **Teste #{r.get('test_id')}:** {r.get('description', r.get('initial_message', '')[:60])}  \n"
                report_md += f"  Slots com loop: {list(r.get('loops_detected', {}).keys())}  \n"
                report_md += f"  Tentativas: {r.get('loops_detected', {})}  \n\n"
        
        # Listar falhas
        failed_cases = [r for r in self.results if not r.get('success') and not r.get('has_loops')]
        if failed_cases:
            report_md += "\n### Falhas Sem Loop\n\n"
            for r in failed_cases[:10]:
                report_md += f"- **Teste #{r.get('test_id')}:** {r.get('description', r.get('initial_message', '')[:60])}  \n"
                if r.get('error'):
                    report_md += f"  Erro: {r.get('error')}  \n\n"
        
        # Salvar relatório
        report_file = f"{output_dir}/report_{self.test_id}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_md)
        
        # Salvar CSV
        csv_file = f"{output_dir}/results_{self.test_id}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'test_id', 'description', 'intent_detected', 'expected_intent',
                'total_turns', 'success', 'has_loops', 'duration_seconds', 'category'
            ])
            writer.writeheader()
            for r in self.results:
                writer.writerow({
                    'test_id': r.get('test_id'),
                    'description': r.get('description', r.get('initial_message', ''))[:100],
                    'intent_detected': r.get('intent_detected'),
                    'expected_intent': r.get('expected_intent'),
                    'total_turns': r.get('total_turns'),
                    'success': r.get('success'),
                    'has_loops': r.get('has_loops'),
                    'duration_seconds': r.get('duration_seconds'),
                    'category': r.get('category')
                })
        
        print(f"📄 Relatório MD: {report_file}")
        print(f"📊 Dados CSV: {csv_file}")
        
        # Print resumo no terminal
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}RESUMO DOS TESTES{Colors.RESET}")
        print(f"{'='*70}")
        print(f"Taxa de sucesso: {Colors.GREEN if success_rate > 80 else Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
        print(f"Turnos médios: {avg_turns:.2f}")
        print(f"Loops detectados: {Colors.RED if with_loops > 0 else Colors.GREEN}{with_loops}{Colors.RESET}")
        print(f"{'='*70}\n")


# Casos de teste baseados em cenários reais
TEST_CASES = [
    # PRINTER_ISSUE
    {
        'description': 'Impressora sem toner - descrição completa',
        'message': 'impressora sem toner na sala 205, ramal 4221',
        'expected_intent': 'PRINTER_ISSUE',
        'category': 'PRINTER_ISSUE',
        'context': {}
    },
    {
        'description': 'Impressora atolou papel - incompleto',
        'message': 'impressora atolou o papel',
        'expected_intent': 'PRINTER_ISSUE',
        'category': 'PRINTER_ISSUE',
        'context': {'location': 'sala 101', 'extension': '4121'}
    },
    {
        'description': 'Impressora não imprime - maiúsculas',
        'message': 'IMPRESSORA NÃO IMPRIME',
        'expected_intent': 'PRINTER_ISSUE',
        'category': 'PRINTER_ISSUE',
        'context': {}
    },
    
    # NETWORK_ISSUE
    {
        'description': 'Sem internet - completo',
        'message': 'estou sem internet aqui na sala 305, ramal 4001',
        'expected_intent': 'NETWORK_ISSUE',
        'category': 'NETWORK_ISSUE',
        'context': {}
    },
    {
        'description': 'WiFi não conecta',
        'message': 'wifi não está conectando',
        'expected_intent': 'NETWORK_ISSUE',
        'category': 'NETWORK_ISSUE',
        'context': {}
    },
    
    # RESET_PASSWORD
    {
        'description': 'Resetar senha - direto',
        'message': 'preciso resetar minha senha do sistema',
        'expected_intent': 'RESET_PASSWORD',
        'category': 'RESET_PASSWORD',
        'context': {}
    },
    {
        'description': 'Esqueci senha',
        'message': 'esqueci a senha',
        'expected_intent': 'RESET_PASSWORD',
        'category': 'RESET_PASSWORD',
        'context': {}
    },
    
    # CREATE_USER
    {
        'description': 'Criar usuário novo estagiário',
        'message': 'criar usuario para novo estagiario',
        'expected_intent': 'CREATE_USER',
        'category': 'CREATE_USER',
        'context': {}
    },
    {
        'description': 'Cadastrar servidor',
        'message': 'preciso cadastrar um novo servidor no AD',
        'expected_intent': 'CREATE_USER',
        'category': 'CREATE_USER',
        'context': {}
    },
    
    # Continuar com mais casos...
]

if __name__ == '__main__':
    tester = TODExhaustiveTester()
    tester.test_batch(TEST_CASES)
