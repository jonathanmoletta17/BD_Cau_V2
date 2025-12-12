import os
import yaml
import json
import requests
import torch
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer, util

from .schemas import ClassificationInput, ClassificationResult

class SurgicalClassifierAgent:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
        self.base_dir = Path(__file__).parent
        
        # 1. Carregar Prompts
        with open(self.base_dir / "prompts.yaml", "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)
            
        # 2. Carregar Taxonomia
        with open(self.base_dir / "taxonomy.yaml", "r", encoding="utf-8") as f:
            self.taxonomy = yaml.safe_load(f)
            
        # 3. Inicializar Modelo de Embeddings (RAG)
        print("🤖 [Classifier] Carregando modelo SentenceTransformer...")
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 4. Pré-cálculo dos Vetores da Taxonomia
        self.corpus_texts = [item['embedding_source'] for item in self.taxonomy]
        self.corpus_embeddings = self.embedder.encode(self.corpus_texts, convert_to_tensor=True)
        print(f"✅ [Classifier] Taxonomia indexada: {len(self.taxonomy)} categorias.")

    def _get_candidates(self, text: str, top_k: int = 5) -> List[Dict]:
        """Etapa 1: Filtro Vetorial (Pré-seleção)"""
        # Prefixo 'query:' ajuda em alguns modelos, mas neste específico não é obrigatório. 
        # Vamos manter simples.
        query_embedding = self.embedder.encode(text, convert_to_tensor=True)
        
        # Busca Semântica (Cosseno)
        cos_scores = util.cos_sim(query_embedding, self.corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.taxonomy)))
        
        candidates = []
        for score, idx in zip(top_results[0], top_results[1]):
            item = self.taxonomy[idx]
            candidates.append({
                "id": item['id'],
                "name": item['name'],
                "description": item['description'],
                "score": float(score)
            })
            
        return candidates

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Chamada compatível com OpenAI API (vLLM)"""
        base_url = os.getenv("LLM_BASE_URL", "http://host.docker.internal:9000/v1").rstrip('/')
        api_url = f"{base_url}/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            # "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ [Classifier] Erro no LLM: {e}")
            if 'response' in locals() and response.text:
                 print(f"Detalhe: {response.text}")
            raise e

    def classify(self, input_data: ClassificationInput) -> ClassificationResult:
        full_text = f"{input_data.summary} {input_data.description}"
        
        # Etapa RAG 1: Top K Candidates
        candidates = self._get_candidates(full_text)
        
        # Formata os candidatos para o Prompt
        candidates_text = ""
        for c in candidates:
            candidates_text += f"- ID: {c['id']} | Nome: {c['name']} (Score: {c['score']:.2f})\n  Desc: {c['description']}\n"
            
        # Etapa RAG 2: LLM Refinement
        system_prompt = self.prompts["system"].format(candidates_text=candidates_text, summary=input_data.summary, description=input_data.description)
        user_prompt = "Classifique agora."
        
        llm_response = self._call_llm(system_prompt, user_prompt)
        
        try:
            clean_response = llm_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_response)
            result = ClassificationResult(**data)
            
            # Etapa 3: Validação / Fuzzy Match (Garantir ID)
            # Verifica se o ID retornado está na lista de candidatos ou taxonomia completa
            valid_id = False
            for item in self.taxonomy:
                if item['id'] == result.category_id:
                    valid_id = True
                    result.category_name = item['name'] # Garante nome oficial
                    break
            
            if not valid_id:
                # Fallback: Se o LLM alucinou um ID, pega o Top 1 do RAG
                print(f"⚠️ [Classifier] LLM alucinou ID {result.category_id}. Revertendo para Top 1 RAG.")
                top_candidate = candidates[0]
                result.category_id = top_candidate['id']
                result.category_name = top_candidate['name']
                result.confidence = top_candidate['score'] # Usa score vetorial como confiança
                result.reasoning = "Fallback para melhor match semântico."
                
            return result
            
        except Exception as e:
            print(f"❌ [Classifier] Erro Parse: {e}")
            # Fallback de erro
            top_1 = candidates[0]
            return ClassificationResult(
                category_id=top_1['id'], 
                category_name=top_1['name'], 
                confidence=0.5, 
                reasoning="Erro no processamento do LLM, retornando melhor match vetorial."
            )
