import time
import sys
import os
from pathlib import Path

# Adiciona o diretório atual ao path para imports funcionarem localmente
# sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'opener'))

from agents.opener.glpi_service import GLPIService
from agents.classifier.agent import SurgicalClassifierAgent
from agents.classifier.schemas import ClassificationInput

class ClassifierDaemon:
    def __init__(self):
        print("🔧 Inicializando Daemon Classificador...")
        self.glpi = GLPIService()
        
        # 1. Carregar Agente AI
        try:
            self.agent = SurgicalClassifierAgent()
            print("🧠 Agente Classificador Carregado.")
        except Exception as e:
            print(f"❌ Erro ao carregar Agente Classificador: {e}")
            sys.exit(1)

        # 2. Sync Check: Mapear Taxonomia -> GLPI IDs
        self.category_map = {} # { "Nome da Taxonomia": ID_GLPI }
        self._sync_categories()

    def _sync_categories(self):
        print("🔄 Sincronizando Categorias com GLPI...")
        glpi_cats = self.glpi.get_all_categories()
        
        # Cria mapa reverso do GLPI {Name: ID}
        # GLPI usually returns "Hardware > Printer". We need to match with taxonomy names.
        glpi_name_map = {c['completename']: c['id'] for c in glpi_cats}
        
        matched_count = 0
        missing_count = 0
        
        for item in self.agent.taxonomy:
            tax_name = item['name']
            
            # Tentativa 1: Match Exato
            if tax_name in glpi_name_map:
                self.category_map[tax_name] = glpi_name_map[tax_name]
                matched_count += 1
            else:
                # Tentativa 2: Aproximação ou Log de Falta
                # Por enqto, apenas logamos. O usuário disse que a taxonomia é a oficial.
                # Se não tem no GLPI, não podemos magicamente adivinhar o ID.
                print(f"⚠️  MISSING IN GLPI: '{tax_name}'")
                missing_count += 1
                
        print(f"✅ Sync Concluído: {matched_count} mapeados, {missing_count} ausentes.")

    def run_loop(self, interval=30):
        print(f"🚀 Daemon Rodando (Intervalo: {interval}s). Pressione Ctrl+C para parar.")
        
        processed_tickets = set()
        
        while True:
            try:
                # Busca tickets recentes (últimos 10 min para garantir)
                recent = self.glpi.get_recent_tickets(minutes=10)
                
                for t in recent:
                    tid = t['id']
                    if tid in processed_tickets:
                        continue
                        
                    # Verifica se precisa classificar
                    # Regra: Se Categoria for 0 (Root) ou vazia ou Genérica (se soubermos ID de genérica)
                    current_cat = t.get('itilcategories_id', 0)
                    
                    # Vamos classificar SEMPRE que for novo para garantir a "Recategorização" pedida
                    print(f"\n🔎 Analisando Ticket #{tid}: {t['name']}")
                    
                    # Prepara Input
                    inp = ClassificationInput(
                        summary=t['name'],
                        description=t['content']
                    )
                    
                    # AI Decide
                    result = self.agent.classify(inp)
                    print(f"   🤖 AI Sugere: {result.category_name} ({result.confidence:.2f})")
                    
                    # Pega ID Real
                    target_id = self.category_map.get(result.category_name)
                    
                    if target_id:
                        if target_id != current_cat:
                            print(f"   📝 Atualizando GLPI: {current_cat} -> {target_id}")
                            self.glpi.update_ticket(tid, target_id)
                        else:
                            print(f"   ✅ Já está na categoria correta.")
                    else:
                        print(f"   ❌ Impossível atualizar: Categoria não existe no GLPI.")
                    
                    processed_tickets.add(tid)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Daemon Parado.")
                break
            except Exception as e:
                print(f"❌ Erro no Loop: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    daemon = ClassifierDaemon()
    daemon.run_loop()
