"""
Ferramenta de Avaliação de Accuracy do Classificador
=====================================================

PROPÓSITO:
    Mede a precisão do classificador usando o dataset de validação.
    Gera relatório detalhado mostrando onde o classificador acerta e erra.

CONCEITOS-CHAVE:
    - Accuracy: Proporção de tickets classificados corretamente
    - Embedding: Representação numérica (vetor) do texto
    - Cosine Similarity: Medida de similaridade entre dois vetores

COMO FUNCIONA:
    1. Carrega o dataset de validação (tickets com categoria correta conhecida)
    2. Para cada ticket:
       a. Gera embedding do texto
       b. Compara com embeddings de todas as categorias
       c. Escolhe a categoria mais similar
       d. Verifica se acertou
    3. Gera relatório com estatísticas

USO:
    python tools/evaluate_accuracy.py

SAÍDA:
    - Resumo no console (accuracy, total de acertos/erros)
    - Arquivo JSON com detalhes de cada classificação
"""

import os
import sys
import json
import torch
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

# Adiciona o diretório raiz ao path para imports locais
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer, util


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

# Dispositivo: GPU se disponível, senão CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Modelo de embedding (mesmo usado no simple_agent.py)
MODEL_NAME = "intfloat/multilingual-e5-large"

# Caminhos dos arquivos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEXT_PATH = os.path.join(PROJECT_ROOT, "agent", "category_context.json")
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports")


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def load_json(path: str) -> any:
    """Carrega um arquivo JSON e retorna seu conteúdo."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: any, path: str) -> None:
    """Salva dados em um arquivo JSON formatado."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_header(title: str) -> None:
    """Imprime um cabeçalho formatado no console."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str) -> None:
    """Imprime uma seção formatada no console."""
    print(f"\n--- {title} ---")


# =============================================================================
# CLASSE PRINCIPAL
# =============================================================================

class AccuracyEvaluator:
    """
    Avaliador de Accuracy do Classificador.
    
    Esta classe encapsula toda a lógica de avaliação, mantendo o código
    organizado e fácil de entender.
    """
    
    def __init__(self):
        """Inicializa o avaliador carregando modelo e dados."""
        print_header("Inicializando Avaliador de Accuracy")
        
        # 1. Verifica disponibilidade de GPU
        print(f"[1/4] Dispositivo: {DEVICE}")
        if DEVICE == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            print(f"      GPU detectada: {gpu_name}")
        
        # 2. Carrega os contextos das categorias
        print(f"[2/4] Carregando contextos de categorias...")
        self.contexts = load_json(CONTEXT_PATH)
        self.categories = list(self.contexts.keys())
        print(f"      {len(self.categories)} categorias carregadas")
        
        # 3. Carrega o dataset de validação
        print(f"[3/4] Carregando dataset de validação...")
        self.dataset = load_json(DATASET_PATH)
        print(f"      {len(self.dataset)} tickets para avaliar")
        
        # 4. Carrega o modelo de embedding
        print(f"[4/4] Carregando modelo de embedding...")
        print(f"      Modelo: {MODEL_NAME}")
        self.model = SentenceTransformer(MODEL_NAME, device=DEVICE)
        print("      Modelo carregado com sucesso!")
        
        # 5. Gera embeddings das categorias
        print("\n[PREP] Gerando embeddings das categorias...")
        self._encode_categories()
        print("       Embeddings prontos!")
    
    def _encode_categories(self) -> None:
        """
        Gera embeddings para todas as categorias.
        
        Usa o mesmo formato do simple_agent.py:
        - Combina nome da categoria com seu contexto
        - Adiciona prefixo "passage:" (convenção do modelo e5)
        """
        passages = []
        for name in self.categories:
            context = self.contexts.get(name, "")
            text_to_embed = f"{name}: {context}" if context else name
            passages.append(f"passage: {text_to_embed}")
        
        self.category_embeddings = self.model.encode(
            passages,
            convert_to_tensor=True,
            device=DEVICE
        )
    
    def classify_text(self, text: str) -> Tuple[str, float]:
        """
        Classifica um texto e retorna a categoria mais provável.
        
        Args:
            text: O texto do ticket a classificar
            
        Returns:
            Tupla (categoria_predita, score_de_confiança)
        """
        # Gera embedding do texto (prefixo "query:" para buscas)
        query_embedding = self.model.encode(
            f"query: {text}",
            convert_to_tensor=True,
            device=DEVICE
        )
        
        # Calcula similaridade com todas as categorias
        scores = util.cos_sim(query_embedding, self.category_embeddings)[0]
        
        # Encontra a categoria com maior score
        best_idx = torch.argmax(scores).item()
        best_score = scores[best_idx].item()
        best_category = self.categories[best_idx]
        
        return best_category, best_score
    

    def evaluate(self, threshold: float = 0.70) -> Dict:
        """
        Executa a avaliação completa do dataset.
        
        Args:
            threshold: Limiar de confiança para considerar uma classificação aceita.
            
        Returns:
            Dicionário com resultados detalhados
        """
        print_header("Executando Avaliação")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "model": MODEL_NAME,
            "device": DEVICE,
            "threshold": threshold,
            "total_categories": len(self.categories),
            "total_tickets": len(self.dataset),
            "correct": 0,
            "incorrect": 0,
            "skipped": 0,
            "skipped_but_correct": 0,  # Seriam corretos, mas foram ignorados
            "accuracy_valid": 0.0,     # Accuracy considerando apenas os não-skipados
            "accuracy_total": 0.0,     # Accuracy sobre todos (skip contam como erro ou neutro?)
            "details": [],
            "errors_by_category": defaultdict(list),
            "confusion_pairs": defaultdict(int)
        }
        
        for i, item in enumerate(self.dataset):
            ticket_id = item.get("id")
            text = item.get("text", "")
            true_category = item.get("true_category", "")
            
            # Classifica o ticket
            predicted_category, confidence = self.classify_text(text)
            
            is_correct = (predicted_category == true_category)
            status = ""
            
            # Lógica de Threshold
            if confidence < threshold:
                results["skipped"] += 1
                if is_correct:
                    results["skipped_but_correct"] += 1
                status = "SKIP"
            else:
                if is_correct:
                    results["correct"] += 1
                    status = "✓"
                else:
                    results["incorrect"] += 1
                    status = "✗"
                    # Registra o erro para análise
                    results["errors_by_category"][true_category].append({
                        "id": ticket_id,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "predicted": predicted_category,
                        "confidence": round(confidence, 4)
                    })
                    # Registra par de confusão
                    pair = f"{true_category} → {predicted_category}"
                    results["confusion_pairs"][pair] += 1
            
            # Armazena detalhes
            results["details"].append({
                "id": ticket_id,
                "true_category": true_category,
                "predicted_category": predicted_category,
                "confidence": round(confidence, 4),
                "correct": is_correct,
                "skipped": (confidence < threshold)
            })
            
            # Mostra progresso a cada 10 tickets
            if (i + 1) % 50 == 0:
                print(f"  Processados: {i + 1}/{len(self.dataset)}")
        
        # Cria métricas finais
        total_valid = results["correct"] + results["incorrect"]
        if total_valid > 0:
            results["accuracy_valid"] = round(results["correct"] / total_valid * 100, 2)
        
        results["accuracy_total"] = round(
            results["correct"] / results["total_tickets"] * 100, 2
        )
        
        # Converte defaultdicts para dicts normais (para JSON)
        results["errors_by_category"] = dict(results["errors_by_category"])
        results["confusion_pairs"] = dict(results["confusion_pairs"])
        
        return results
    
    def print_report(self, results: Dict) -> None:
        """Imprime relatório formatado no console."""
        
        print_header("RELATÓRIO DE ACCURACY")
        
        # Resumo geral
        print_section("Resumo")
        print(f"  Total de tickets:      {results['total_tickets']}")
        print(f"  Threshold:             {results['threshold']}")
        print(f"  Skipped (ignorado):    {results['skipped']} ({(results['skipped']/results['total_tickets'])*100:.1f}%)")
        print(f"  Classificados:         {results['correct'] + results['incorrect']}")
        print(f"    - Acertos:           {results['correct']}")
        print(f"    - Erros:             {results['incorrect']}")
        print("-" * 30)
        print(f"  PRECISÃO (nos classificados):  {results['accuracy_valid']}%")
        print("-" * 30)
        
        # Top 5 pares de confusão
        if results["confusion_pairs"]:
            print_section("Top 5 Erros Mais Frequentes")
            sorted_pairs = sorted(
                results["confusion_pairs"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for pair, count in sorted_pairs:
                print(f"  {count}x: {pair}")
        
        # Categorias com mais erros
        if results["errors_by_category"]:
            print_section("Categorias com Mais Erros")
            sorted_cats = sorted(
                results["errors_by_category"].items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5]
            for cat, errors in sorted_cats:
                print(f"  {len(errors)} erros: {cat}")
        
        print("\n" + "=" * 60)


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def main():
    """Função principal que executa a avaliação."""
    
    # Cria o avaliador
    evaluator = AccuracyEvaluator()
    
    # Executa avaliação
    results = evaluator.evaluate()
    
    # Imprime relatório no console
    evaluator.print_report(results)
    
    # Salva relatório detalhado em JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"accuracy_report_{timestamp}.json")
    save_json(results, output_path)
    print(f"\n📄 Relatório salvo em: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
