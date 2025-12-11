"""
Máquina de Estados Finitos (FSM) para Abertura de Tickets
Versão Standalone - Testável sem dependências do projeto

Este módulo pode ser testado isoladamente antes de integração no agent.py.
Ele foca em CORRIGIR as regras de negócio (Urgência, Local, Impacto) que o LLM erra.
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field
import re

# ==========================================
# 1. Definições de Dados
# ==========================================

class Urgency(str, Enum):
    HIGH = "Alta"
    MEDIUM = "Média"
    LOW = "Baixa"

class Impact(str, Enum):
    INDIVIDUAL = "Individual"
    SECTOR = "Setorial"
    ORG = "Organizacional"

@dataclass
class TicketContext:
    original_complaint: str
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    intent: Optional[str] = None
    missing_info: List[str] = field(default_factory=list)
    response_to_user: Optional[str] = None
    ready_to_submit: bool = False
    
    # Histórico de conversas para contexto (Simulação)
    history: List[str] = field(default_factory=list)

# ==========================================
# 2. Motor de Regras (The Brain)
# ==========================================

class TicketFSM:
    def __init__(self):
        # Regras de Palavras-Chave (Simples e Eficiente)
        self.rules = {
            "password_reset": {
                "keywords": ["senha", "bloquead", "acesso", "token", "login"],
                "urgency": Urgency.HIGH,   # Bloqueio é sempre Alta
                "impact": Impact.INDIVIDUAL,
                "required": ["location"] # Mesmo bloqueio precisa saber onde está (físico ou home)
            },
            "internet_issue": {
                "keywords": ["internet", "wifi", "wi-fi", "rede", "conexão", "lenta", "cair"],
                "urgency": Urgency.MEDIUM, # Lenta = Media. Parada = Alta (refinar depois)
                "impact": Impact.SECTOR,   # Rede geralmente afeta setor
                "required": ["location"]
            },
            "hardware_request": {
                "keywords": ["fone", "mouse", "teclado", "monitor", "desktop", "computador", "equipamento", "cabo"],
                "urgency": Urgency.LOW,    # Requisição material = Baixa (padrão)
                "impact": Impact.INDIVIDUAL,
                "required": ["location", "quantity"]
            },
            "email_issue": {
                "keywords": ["email", "e-mail", "outlook", "caixa", "compartilhada"],
                "urgency": Urgency.LOW,
                "impact": Impact.INDIVIDUAL,
                "required": [] # Email geralmente é remoto, mas location ajuda
            }
        }

    def _detect_intent(self, text: str) -> str:
        """Heurística simples para detectar intenção baseada em keywords"""
        text = text.lower()
        
        # Ordem de prioridade
        if any(w in text for w in self.rules["password_reset"]["keywords"]):
            return "password_reset"
        if any(w in text for w in self.rules["internet_issue"]["keywords"]):
            return "internet_issue"
        if any(w in text for w in self.rules["hardware_request"]["keywords"]):
            return "hardware_request"
        if any(w in text for w in self.rules["email_issue"]["keywords"]):
            return "email_issue"
            
        return "general_support"

    def _extract_location(self, text: str) -> Optional[str]:
        """Tenta extrair local do texto (Sala, Prédio, Setor)"""
        # Regex ingênuo para demo - O LLM faria isso melhor, mas aqui valido a lógica
        patterns = [
            r"(sala\s+\d+)",
            r"(andar\s+\d+)",
            r"(casa civil)",
            r"(rh|recursos humanos)",
            r"(prédio\s+\w+)",
            r"(departamento\s+\w+)"
        ]
        text_lower = text.lower()
        for p in patterns:
            match = re.search(p, text_lower)
            if match:
                return match.group(1).title()
        return None

    def process_input(self, ctx: TicketContext, user_input: str, llm_data: Dict = None) -> TicketContext:
        """
        Processa o input do usuário e atualiza o estado do ticket.
        Esta função substitui a lógica "cega" do LLM atual.
        Pode receber dados pré-processados pelo LLM (llm_data) para refinar a extração.
        """
        # 1. Update Descrição / Histórico
        if not ctx.description:
            ctx.description = user_input
        ctx.history.append(f"User: {user_input}")

        # 2. Detectar Intenção (Se ainda não tem)
        extracted_intent = None
        if llm_data and "intent" in llm_data:
             extracted_intent = llm_data["intent"]
        
        if not ctx.intent:
            ctx.intent = extracted_intent or self._detect_intent(ctx.description)

        # 3. Aplicar Regras da Intenção (Defaults)
        rule = self.rules.get(ctx.intent)
        if rule:
            if not ctx.urgency:
                ctx.urgency = rule["urgency"]
            if not ctx.impact:
                ctx.impact = rule["impact"]

        # 4. Extração de Entidades (Slots) do INPUT ATUAL
        # Prioriza Regex (Mais confiável/Validado), Fallback para LLM
        current_loc = self._extract_location(user_input)
        
        if not current_loc:
             # Se regex não pegou, vê se o LLM achou algo útil
             if llm_data and "location" in llm_data and llm_data["location"]:
                 # TODO: Adicionar validação aqui para evitar alucinação "insira local aqui"
                 current_loc = llm_data["location"]

        if current_loc:
            ctx.location = current_loc

        # 5. Validação de Requisitos (Onde a mágica acontece)
        missing = []
        
        # Validar Localização
        if not ctx.location:
            # Regra: Se é hardware ou rede, PRECISA de local
            if ctx.intent in ["hardware_request", "internet_issue"]:
                missing.append("location")
            # Senha/Email pode ser debatível, mas vamos pedir se não tiver
            elif ctx.intent == "password_reset" and not ctx.location:
                 missing.append("location")

        # Validar Quantidade (Exemplo Hardware) e Item
        # (Simplificado para este teste)

        ctx.missing_info = missing

        # 6. Gerar Resposta / Próximo Passo
        if "location" in missing:
            ctx.response_to_user = "Para onde você pertence (Prédio, Andar e Sala)?"
            ctx.ready_to_submit = False
        else:
            # Se não falta nada crítico, montamos o resumo
            ctx.summary = f"Solicitação: {ctx.intent.replace('_', ' ').title()}" 
            if ctx.location:
                ctx.summary += f" - {ctx.location}"
            
            ctx.response_to_user = (
                f"Entendi. Vou abrir um chamado para '{ctx.summary}'. \n"
                f"Urgência definida como: {ctx.urgency}. De acordo?"
            )
            ctx.ready_to_submit = True # Em teoria espera o 'Sim', mas para FSM teste = Pronto

        return ctx

# Helper para testar conversa
def simulate_conversation(inputs: List[str]) -> TicketContext:
    fsm = TicketFSM()
    ctx = TicketContext(original_complaint=inputs[0])
    
    print(f"\n--- Simulação: {inputs[0][:40]}... ---")
    
    for i, text in enumerate(inputs):
        print(f"User [{i}]: {text}")
        ctx = fsm.process_input(ctx, text)
        print(f"Agent: {ctx.response_to_user}")
        if ctx.ready_to_submit:
            print(">> Ticket Pronto!")
            break
            
    return ctx
