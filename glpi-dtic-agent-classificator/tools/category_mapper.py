"""
Category Mapper - Fuzzy String Matching para Categorias GLPI

Este módulo fornece mapeamento inteligente de categorias textuais (vindas do LLM)
para IDs numéricos do GLPI usando fuzzy string matching.

Uso:
    from tools.category_mapper import CategoryMapper
    
    cat_map = client.categories_map()
    mapper = CategoryMapper(cat_map, threshold=85)
    
    category_id = mapper.map_to_id("Impressora")
    # Retorna ID se match >= 85%, caso contrário None
"""

from typing import Optional, Dict, List, Tuple
from rapidfuzz import fuzz, process


class CategoryMapper:
    """
    Mapeamento fuzzy de categorias textuais para IDs GLPI.
    
    Utiliza o algoritmo de Levenshtein Distance via RapidFuzz para encontrar
    a melhor correspondência entre texto livre e categorias oficiais do GLPI.
    """
    
    def __init__(self, categories_map: Dict[str, int], threshold: int = 85):
        """
        Inicializa o mapeador de categorias.
        
        Args:
            categories_map: Dicionário {nome_completo_categoria: id_glpi}
                           Obtido via GlpiClient.categories_map()
            threshold: Score mínimo (0-100) para aceitar um match.
                      Valores recomendados:
                      - 90+: Muito restritivo, apenas matches quase exatos
                      - 85: Recomendado (padrão)
                      - 70-84: Permissivo, pode gerar false positives
        """
        self.cat_map = categories_map
        self.threshold = threshold
        self.last_match_info = None  # Para debugging
    
    def map_to_id(self, category_text: str, verbose: bool = True) -> Optional[int]:
        """
        Mapeia texto livre para ID de categoria GLPI.
        
        Args:
            category_text: Texto da categoria sugerida (ex: "Impressora")
            verbose: Se True, imprime informações do matching
        
        Returns:
            ID numérico da categoria se match >= threshold, caso contrário None
        
        Examples:
            >>> mapper.map_to_id("Impressora")
            ✅ Category Match: 'Impressora' → '1. Hardware e Impressão > Impressoras e Scanners' (score: 95)
            5671
            
            >>> mapper.map_to_id("xyz123")
            ⚠️ No confident match for: 'xyz123' (best score: 12)
            None
        """
        if not category_text or not self.cat_map:
            return None
        
        # Fuzzy match usando partial_ratio (permite substring matching)
        result = process.extractOne(
            category_text.strip(),
            self.cat_map.keys(),
            scorer=fuzz.partial_ratio
        )
        
        # Armazena info do último match para debugging
        self.last_match_info = result
        
        if result and result[1] >= self.threshold:
            category_name = result[0]
            category_id = self.cat_map[category_name]
            
            if verbose:
                print(f"✅ Category Match: '{category_text}' → '{category_name}' (score: {result[1]})")
            
            return category_id
        else:
            if verbose:
                best_score = result[1] if result else 0
                print(f"⚠️ No confident match for: '{category_text}' (best score: {best_score})")
            
            return None
    
    def get_top_matches(self, category_text: str, limit: int = 5) -> List[Tuple[str, int, int]]:
        """
        Retorna os top N matches mais prováveis.
        
        Útil para debugging ou para permitir que o usuário escolha manualmente.
        
        Args:
            category_text: Texto a buscar matches
            limit: Número máximo de resultados
        
        Returns:
            Lista de tuplas (categoria_nome, score, indice)
            Ordenada por score descendente
        
        Example:
            >>> matches = mapper.get_top_matches("Impressora", limit=3)
            >>> for name, score, _ in matches:
            ...     print(f"{score}%: {name}")
            95%: 1. Hardware e Impressão > Impressoras e Scanners
            78%: 1. Hardware e Impressão > Periféricos
            65%: 3. Software e Sistemas > Outros Softwares
        """
        if not category_text or not self.cat_map:
            return []
        
        results = process.extract(
            category_text.strip(),
            self.cat_map.keys(),
            scorer=fuzz.partial_ratio,
            limit=limit
        )
        
        return results
    
    def get_match_details(self) -> Optional[Dict]:
        """
        Retorna detalhes do último match realizado.
        
        Returns:
            Dict com informações do match ou None se nenhum match foi feito
        """
        if not self.last_match_info:
            return None
        
        category_name, score, _ = self.last_match_info
        
        return {
            "matched_category": category_name,
            "score": score,
            "category_id": self.cat_map.get(category_name),
            "confidence": "high" if score >= 90 else "medium" if score >= self.threshold else "low",
            "accepted": score >= self.threshold
        }


# Função de conveniência para uso rápido
def quick_category_match(categories_map: Dict[str, int], 
                         category_text: str, 
                         threshold: int = 85) -> Optional[int]:
    """
    Função helper para matching rápido sem criar instância.
    
    Args:
        categories_map: Dicionário de categorias do GLPI
        category_text: Texto a mapear
        threshold: Score mínimo
    
    Returns:
        ID da categoria ou None
    """
    mapper = CategoryMapper(categories_map, threshold)
    return mapper.map_to_id(category_text, verbose=False)


if __name__ == "__main__":
    # Exemplo de uso standalone
    print("=== CategoryMapper Test ===\n")
    
    # Mock de categorias para demonstração
    mock_categories = {
        "1. Hardware e Impressão > Impressoras e Scanners": 5671,
        "1. Hardware e Impressão > Periféricos": 1234,
        "2. Acesso e Identidade > Senhas e Desbloqueio": 4567,
        "3. Software e Sistemas > Office 365 e Email": 7890,
        "4. Rede e Conectividade > Internet e Wi-Fi": 3456,
    }
    
    mapper = CategoryMapper(mock_categories, threshold=85)
    
    # Test cases
    test_cases = [
        "Impressora",
        "Wi-Fi",
        "Email",
        "Senha",
        "Mouse",
        "xyz123"
    ]
    
    for test in test_cases:
        print(f"\nTesting: '{test}'")
        category_id = mapper.map_to_id(test)
        print(f"Result: {category_id}")
        
        # Mostrar top 3 matches
        print("Top 3 matches:")
        for name, score, _ in mapper.get_top_matches(test, limit=3):
            print(f"  {score:>3}%: {name}")
