from agents.classifier.agent import SurgicalClassifierAgent
from agents.classifier.schemas import ClassificationInput
import time

def test_classifier():
    print("\n🔹 Iniciando Teste do Classificador Híbrido (RAG)...")
    
    # 1. Inicialização (Vai baixar o modelo na primeira vez)
    start_time = time.time()
    agent = SurgicalClassifierAgent()
    print(f"✅ Agente Inicializado em {time.time() - start_time:.2f}s")
    
    # 2. Casos de Teste
    test_cases = [
        ("Mouse com defeito", "O botão esquerdo do meu mouse parou de clicar e a luz vermelha está piscando."),
        ("Erro no PROA", "Não consigo acessar o sistema PROA, aparece erro de credenciais inválidas ao tentar logar."),
        ("Senha Bloqueada", "Esqueci minha senha de rede e bloqueei minha conta após 3 tentativas.")
    ]
    
    for summary, desc in test_cases:
        print(f"\n🔸 Testando: [{summary}]")
        inp = ClassificationInput(summary=summary, description=desc)
        
        t0 = time.time()
        result = agent.classify(inp)
        duration = time.time() - t0
        
        print(f"   🏆 Categoria: {result.category_name}")
        print(f"   🆔 ID: {result.category_id}")
        print(f"   🎯 Confiança: {result.confidence:.2f}")
        print(f"   🧠 Razão: {result.reasoning}")
        print(f"   ⏱️ Tempo: {duration:.2f}s")

if __name__ == "__main__":
    test_classifier()
