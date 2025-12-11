import os
import requests
import json
import datetime
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis do .env na raiz (ajuste o path conforme necessário)
# Assumindo que o .env está duas pastas acima (glpi-ai-system/.env)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

GLPI_URL = os.getenv("GLPI_TEST_URL")
USER_TOKEN = os.getenv("GLPI_TEST_USER_TOKEN")
APP_TOKEN = os.getenv("GLPI_TEST_APP_TOKEN")

class GLPIService:
    def __init__(self):
        if not all([GLPI_URL, USER_TOKEN, APP_TOKEN]):
            print("⚠️ AVISO: Credenciais GLPI incompletas no .env")
        
        self.base_url = GLPI_URL
        self.headers = {
            "App-Token": APP_TOKEN,
            "Authorization": f"user_token {USER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.session_token = None

    def init_session(self):
        """Inicia sessão e obtém o Session-Token"""
        try:
            url = f"{self.base_url}/initSession"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            self.session_token = response.json().get("session_token")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar sessão GLPI: {e}")
            return False

    def kill_session(self):
        """Encerra a sessão"""
        if not self.session_token:
            return
        try:
            url = f"{self.base_url}/killSession"
            headers = self.headers.copy()
            headers["Session-Token"] = self.session_token
            requests.get(url, headers=headers)
        except:
            pass

    def create_ticket(self, title: str, description: str, location: str = None, urgency: str = "Média"):
        """Cria um chamado simples"""
        if not self.session_token:
            if not self.init_session():
                return {"error": "Falha na autenticação"}

        # Mapeamento simples de Urgência (GLPI usa 1 a 5)
        # 1=Muto Baixa, 2=Baixa, 3=Média, 4=Alta, 5=Muito Alta
        urgency_map = {
            "Baixa": 2,
            "Média": 3,
            "Alta": 4
        }
        glpi_urgency = urgency_map.get(urgency, 3)

        payload = {
            "input": {
                "name": title,
                "content": f"{description}\n\n[Local]: {location if location else 'Não informado'}\n[Criado por Agente IA]",
                "urgency": glpi_urgency,
                # "itilcategories_id": ... (Poderíamos inferir, mas vamos deixar padrão)
            }
        }

        url = f"{self.base_url}/Ticket"
        headers = self.headers.copy()
        headers["Session-Token"] = self.session_token

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erro ao criar ticket: {e}")
            if response is not None:
                print(f"Detalhes: {response.text}")
            return {"error": str(e)}
    def get_all_categories(self):
        """Busca TODAS as categorias para montar o mapa Nome -> ID"""
        if not self.session_token:
            if not self.init_session():
                return []
        
        url = f"{self.base_url}/ITILCategory?range=0-1000" # Tenta pegar todas (ajustar range se necessário)
        headers = self.headers.copy()
        headers["Session-Token"] = self.session_token
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erro ao buscar categorias: {e}")
            return []

    def get_recent_tickets(self, minutes: int = 5):
        """Busca tickets criados nos últimos X minutos"""
        if not self.session_token:
            if not self.init_session():
                return []
                
        # GLPI Search Criteria é complexo, vamos simplificar pegando os ultimos N e filtrando por data se possível
        # Ou range=0-20 ordenado por ID DESC (os mais novos primeiro)
        url = f"{self.base_url}/Ticket?range=0-20&sort=id&order=DESC"
        headers = self.headers.copy()
        headers["Session-Token"] = self.session_token
        
        recent_tickets = []
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            tickets = response.json()
            
            # Filtro Manual de Tempo (Já que a API de search é chata)
            now = datetime.datetime.now()
            limit_time = now - timedelta(minutes=minutes)
            
            for t in tickets:
                # date_creation format: "2024-12-10 14:00:00"
                try:
                    t_time = datetime.datetime.strptime(t['date_creation'], "%Y-%m-%d %H:%M:%S")
                    if t_time >= limit_time:
                        recent_tickets.append(t)
                except:
                    # Se falhar parse, ignora ou inclui (segurança)
                    pass
                    
            return recent_tickets
        except Exception as e:
            print(f"❌ Erro ao buscar tickets recentes: {e}")
            return []

    def update_ticket(self, ticket_id: int, category_id: int, reason: str = None):
        """Atualiza a categoria de um ticket"""
        if not self.session_token:
            if not self.init_session():
                return False
                
        url = f"{self.base_url}/Ticket/{ticket_id}"
        headers = self.headers.copy()
        headers["Session-Token"] = self.session_token
        
        # Payload de Atualização
        payload = {
            "input": {
                "itilcategories_id": category_id
            }
        }
        
        # Se quiser adicionar um comentário sobre a mudança (Opcional)
        # GLPI API não deixa comentar no PUT do Ticket geralmente, precisa de endpoint /Ticket/id/ITILSolution ou algo assim
        # Por enquanto mudamos só a categoria.
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ Ticket {ticket_id} atualizado para Categoria {category_id}")
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar ticket {ticket_id}: {e}")
            return False
