#!/usr/bin/env python3
"""
Script de teste de inferência para vLLM
Reproduz o erro HTTP 500 relatado no endpoint /v1/chat/completions
"""
import requests
import json
import time

def test_health():
    """Testa endpoint de health"""
    print("=" * 60)
    print("🔍 Testando /health")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_models():
    """Lista modelos disponíveis"""
    print("\n" + "=" * 60)
    print("📋 Testando /v1/models")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:9000/v1/models", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Modelos disponíveis:")
            for model in data.get("data", []):
                print(f"  - {model.get('id')}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_chat_completion():
    """Testa inferência no endpoint /v1/chat/completions"""
    print("\n" + "=" * 60)
    print("💬 Testando /v1/chat/completions (REPRODUZINDO ERRO)")
    print("=" * 60)
    
    payload = {
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ",
        "messages": [
            {"role": "user", "content": "Olá, responda apenas 'OK'"}
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("Enviando requisição...")
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:9000/v1/chat/completions",
            json=payload,
            timeout=60
        )
        duration = time.time() - start
        
        print(f"\n⏱️  Tempo de resposta: {duration:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📦 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCESSO!")
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            print(f"Response Body:")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Servidor não respondeu em 60s")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {type(e).__name__}: {e}")
        return False

def main():
    print("\n🚀 INICIANDO BATERIA DE TESTES vLLM")
    print("Target: http://localhost:9000")
    print("Modelo: Qwen/Qwen2.5-Coder-7B-Instruct-AWQ\n")
    
    # Teste 1: Health
    health_ok = test_health()
    if not health_ok:
        print("\n⚠️  Health check falhou. Container pode não estar pronto.")
        print("Execute: docker logs glpi-vllm-awq --tail 20")
        return
    
    # Teste 2: Models
    models_ok = test_models()
    
    # Teste 3: Inferência (onde o erro ocorre)
    inference_ok = test_chat_completion()
    
    # Sumário
    print("\n" + "=" * 60)
    print("📊 SUMÁRIO DOS TESTES")
    print("=" * 60)
    print(f"Health Check:       {'✅' if health_ok else '❌'}")
    print(f"Models Endpoint:    {'✅' if models_ok else '❌'}")
    print(f"Chat Completion:    {'✅' if inference_ok else '❌'}")
    
    if not inference_ok:
        print("\n⚠️  ERRO DETECTADO!")
        print("Possíveis causas:")
        print("1. Compilação JIT do Triton falhando (subprocess.CalledProcessError)")
        print("2. Incompatibilidade CUDA/Driver no WSL2")
        print("3. Flags de quantização incorretas para AWQ")
        print("\n💡 Próximos passos:")
        print("1. docker logs glpi-vllm-awq --tail 100")
        print("2. Verificar mensagem de erro específica do Triton/GCC")
        print("3. Considerar migração de '--quantization awq' para 'awq_marlin'")

if __name__ == "__main__":
    main()
