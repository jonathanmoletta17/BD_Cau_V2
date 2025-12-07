"""
Gerador Automático de Contextos Ricos
=====================================

PROPÓSITO:
    Analisa os tickets do dataset de validação e gera contextos ricos
    para cada categoria baseado nos termos que realmente aparecem nos tickets.

ESTRATÉGIA:
    1. Agrupa tickets por categoria verdadeira
    2. Extrai termos mais frequentes e relevantes de cada grupo
    3. Gera contexto descritivo usando esses termos
    4. Adiciona diferenciadores para categorias pai/filho

TÉCNICA:
    - TF-IDF para encontrar termos mais distintivos
    - Análise de n-gramas (palavras compostas)
    - Template estruturado para consistência

USO:
    python tools/generate_rich_contexts.py
"""

import os
import sys
import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Caminhos dos arquivos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")
CONTEXT_PATH = os.path.join(PROJECT_ROOT, "agent", "category_context.json")
BACKUP_PATH = os.path.join(PROJECT_ROOT, "agent", "category_context_BACKUP.json")


# =============================================================================
# FUNÇÕES DE PROCESSAMENTO DE TEXTO
# =============================================================================

def normalize_text(text: str) -> str:
    """Normaliza texto: minúsculas, remove pontuação excessiva."""
    text = text.lower()
    # Remove emails e telefones (ruído)
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
    text = re.sub(r'\d{8,}', '', text)
    # Remove pontuação dupla
    text = re.sub(r'[^\w\sáàâãéèêíïóôõöúçñ]', ' ', text)
    # Remove espaços múltiplos
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_terms(text: str, min_length: int = 3) -> List[str]:
    """
    Extrai termos relevantes do texto.
    
    Retorna palavras e bigramas (2 palavras juntas).
    """
    text = normalize_text(text)
    words = text.split()
    
    # Stopwords em português (simplificado)
    stopwords = {
        'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com',
        'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como',
        'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser',
        'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo',
        'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo',
        'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você',
        'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm',
        'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho',
        'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele'
    }
    
    # Palavras únicas
    terms = []
    for word in words:
        if len(word) >= min_length and word not in stopwords:
            terms.append(word)
    
    # Bigramas (2 palavras juntas)
    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if (len(w1) >= min_length and len(w2) >= min_length and 
            w1 not in stopwords and w2 not in stopwords):
            bigrams.append(f"{w1} {w2}")
    
    return terms + bigrams


# =============================================================================
# ANÁLISE DE TICKETS POR CATEGORIA
# =============================================================================

class ContextGenerator:
    """Gera contextos ricos baseados em análise de tickets."""
    
    def __init__(self):
        """Inicializa o gerador carregando o dataset."""
        print("=" * 60)
        print("  GERADOR AUTOMÁTICO DE CONTEXTOS RICOS")
        print("=" * 60)
        
        # Carrega dataset de validação
        print("\n[1/5] Carregando dataset de validação...")
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)
        print(f"      {len(self.dataset)} tickets carregados")
        
        # Agrupa tickets por categoria
        print("[2/5] Agrupando tickets por categoria...")
        self.tickets_by_category = defaultdict(list)
        for item in self.dataset:
            cat = item.get("true_category")
            text = item.get("text", "")
            if cat and text:
                self.tickets_by_category[cat].append(text)
        
        print(f"      {len(self.tickets_by_category)} categorias distintas")
        
        # Carrega estrutura de categorias completa (do arquivo antigo)
        print("[3/5] Carregando todas as categorias...")
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            old_contexts = json.load(f)
        self.all_categories = list(old_contexts.keys())
        print(f"      {len(self.all_categories)} categorias totais")
    
    def extract_category_terms(self, category: str) -> List[Tuple[str, int]]:
        """
        Extrai os termos mais relevantes para uma categoria.
        
        Returns:
            Lista de (termo, frequência) ordenada por relevância
        """
        tickets = self.tickets_by_category.get(category, [])
        
        if not tickets:
            # Categoria sem exemplos no dataset
            return []
        
        # Extrai todos os termos de todos os tickets
        all_terms = []
        for ticket in tickets:
            all_terms.extend(extract_terms(ticket))
        
        # Conta frequências
        term_counts = Counter(all_terms)
        
        # Retorna top 15 termos mais frequentes
        return term_counts.most_common(15)
    
    def generate_context(self, category: str) -> str:
        """
        Gera contexto rico para uma categoria.
        
        Args:
            category: Nome da categoria
            
        Returns:
            String com o contexto gerado
        """
        # Extrai termos da categoria
        top_terms = self.extract_category_terms(category)
        
        # Identifica se é categoria pai ou filha
        is_parent = any(cat.startswith(category + " >") for cat in self.all_categories)
        has_parent = " > " in category
        
        # Constrói o contexto
        parts = []
        
        # 1. Descrição básica
        if top_terms:
            main_terms = [t for t, _ in top_terms[:5]]
            parts.append(f"Tickets relacionados a: {', '.join(main_terms)}.")
        else:
            # Fallback: usa o nome da categoria
            last_part = category.split(" > ")[-1]
            parts.append(f"Tickets relacionados a {last_part}.")
        
        # 2. Termos-chave específicos
        if top_terms and len(top_terms) > 5:
            additional_terms = [t for t, _ in top_terms[5:10]]
            if additional_terms:
                parts.append(f"Termos comuns: {', '.join(additional_terms)}.")
        
        # 3. Diferenciadores para categorias pai
        if is_parent:
            children = [cat for cat in self.all_categories if cat.startswith(category + " >")]
            if len(children) <= 3:
                child_names = [c.split(" > ")[-1] for c in children]
                parts.append(f"Use esta categoria apenas se NÃO for especificamente sobre: {', '.join(child_names)}.")
            else:
                parts.append("Use esta categoria apenas para casos GERAIS que não se encaixam em subcategorias específicas.")
        
        # 4. Indicação de categoria filha
        if has_parent:
            parts.append("Categoria específica - use quando o ticket mencionar claramente este assunto.")
        
        return " ".join(parts)
    

    def load_manual_contexts(self) -> Dict[str, str]:
        """Carrega contextos manuais se existirem."""
        manual_path = os.path.join(PROJECT_ROOT, "agent", "manual_contexts.json")
        if os.path.exists(manual_path):
            with open(manual_path, "r", encoding="utf-8") as f:
                print(f"[EXTRA] Carregando contextos manuais de: {manual_path}")
                return json.load(f)
        return {}

    def generate_all_contexts(self) -> Dict[str, str]:
        """Gera contextos para todas as categorias, respeitando manuais."""
        print("\n[4/5] Gerando contextos para todas as categorias...")
        
        manual_contexts = self.load_manual_contexts()
        contexts = {}
        categories_with_data = 0
        categories_without_data = 0
        manual_overrides = 0
        
        for category in self.all_categories:
            # 1. Checa se há override manual
            if category in manual_contexts:
                contexts[category] = manual_contexts[category]
                manual_overrides += 1
                if category in self.tickets_by_category:
                    categories_with_data += 1
            else:
                # 2. Gera automaticamente
                context = self.generate_context(category)
                contexts[category] = context
                
                if category in self.tickets_by_category:
                    categories_with_data += 1
                else:
                    categories_without_data += 1
        
        print(f"      Contextos finais:")
        print(f"      - Manuais (Override): {manual_overrides}")
        print(f"      - Automáticos (Com dados): {categories_with_data - manual_overrides}")
        print(f"      - Automáticos (Sem dados): {categories_without_data}")
        
        return contexts
    
    def save_contexts(self, contexts: Dict[str, str]) -> None:
        """Salva os novos contextos, criando backup do arquivo antigo."""
        print("\n[5/5] Salvando novos contextos...")
        
        # Backup do arquivo original
        if os.path.exists(CONTEXT_PATH):
            with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            with open(BACKUP_PATH, "w", encoding="utf-8") as f:
                json.dump(old_data, f, indent=2, ensure_ascii=False)
            print(f"      Backup salvo em: category_context_BACKUP.json")
        
        # Salva novos contextos
        with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
            json.dump(contexts, f, indent=2, ensure_ascii=False)
        
        print(f"      Novos contextos salvos em: category_context.json")
        print("\n✓ Concluído!")
    
    def show_sample(self, contexts: Dict[str, str], n: int = 5) -> None:
        """Mostra amostra de contextos gerados, priorizando manuais."""
        print("\n" + "=" * 60)
        print("  AMOSTRA DE CONTEXTOS")
        print("=" * 60)
        
        manual_ctx = self.load_manual_contexts()
        
        # Mostra os manuais primeiro
        for cat in manual_ctx:
            if cat in contexts:
                print(f"\n[MANUAL] {cat}")
                print(f"    → {contexts[cat]}")
        
        # Mostra alguns outros
        count = 0
        for cat, ctx in contexts.items():
            if cat not in manual_ctx and count < n:
                print(f"\n[AUTO] {cat}")
                print(f"    → {ctx}")
                count += 1


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def main():
    """Função principal."""
    generator = ContextGenerator()
    
    # Gera contextos
    new_contexts = generator.generate_all_contexts()
    
    # Mostra amostra
    generator.show_sample(new_contexts, n=3)
    
    # Salva
    generator.save_contexts(new_contexts)
    
    print("\n" + "=" * 60)
    print("Próximo passo: Executar 'python tools/evaluate_accuracy.py'")
    print("para medir a nova accuracy!")
    print("=" * 60)


if __name__ == "__main__":
    main()
