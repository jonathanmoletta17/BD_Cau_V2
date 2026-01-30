# Stack NVIDIA para IA: Mapeamento Conceitual

O projeto utiliza tecnologias NVIDIA para acelerar o processamento. Este documento desmistifica essa "sopa de letrinhas" e explica onde cada peça se encaixa.

---

## 1. Componentes Fundamentais

### CUDA (Compute Unified Device Architecture)
*   **O que é:** A base de tudo. É a linguagem que permite que programas falem diretamente com a placa de vídeo (GPU).
*   **No nosso projeto:** O PyTorch (biblioteca de IA) usa CUDA por baixo dos panos para fazer as contas de matrizes dos embeddings. Sem CUDA, a geração de embeddings seria 20x a 50x mais lenta (rodando na CPU).

### cuDNN (CUDA Deep Neural Network library)
*   **O que é:** Uma biblioteca de primitivas otimizadas para redes neurais.
*   **No nosso projeto:** Acelera operações específicas de Deep Learning (convoluções, atenção) que o modelo Transformer (BERT/E5) usa intensamente.

---

## 2. Componentes de Otimização e Inferência

### TensorRT
*   **O que é:** Um otimizador de modelos. Ele pega o seu modelo "pesado" (PyTorch) e o compila para rodar o mais rápido possível na sua placa específica.
*   **Benefício:** Reduz a latência (tempo de resposta). Pode fazer um modelo responder em 2ms em vez de 10ms.
*   **Uso potencial:** Se tivermos um volume massivo de tickets (milhares por minuto), converter o modelo de embedding para TensorRT seria vital. Para volume baixo, é opcional.

### Triton Inference Server
*   **O que é:** Um servidor de "modelos como serviço". Em vez de carregar o modelo dentro do script Python, você sobe o Triton e o script apenas manda requisições para ele.
*   **Benefício:**
    *   **Escalabilidade:** Pode atender vários scripts ao mesmo tempo.
    *   **Dynamic Batching:** Junta 10 tickets que chegaram ao mesmo tempo e processa todos de uma vez na GPU (muito mais eficiente).
*   **No nosso projeto:** Seria a evolução da arquitetura. O `agent/simple_agent.py` deixaria de carregar o modelo (ficaria leve) e apenas chamaria o Triton.

---

## 3. Mapeamento no Fluxo de Classificação

| Componente | Onde entra? | Função Principal | Impacto no Negócio |
| :--- | :--- | :--- | :--- |
| **GPU NVIDIA** | Hardware | Executar cálculos paralelos massivos. | Viabiliza uso de modelos modernos (Transformers) em tempo real. |
| **CUDA / cuDNN** | Driver/Lib | Traduzir PyTorch para a GPU. | Performance base. Sem eles, o sistema seria lento demais. |
| **PyTorch (com CUDA)** | Aplicação | Rodar o modelo de Embedding (E5/BERT). | É o motor atual do agente. |
| **TensorRT** | Otimização | (Futuro) Compilar o modelo. | Reduzir custo de nuvem (precisa de menos GPU para mesmo volume). |
| **Triton** | Serviço | (Futuro) Servir o modelo via API. | Permitir que GLPI, Chatbot e Site usem a mesma IA simultaneamente. |

---

## 4. Recomendação de Uso Atual

Para o estágio atual (validação e piloto), a stack **PyTorch + CUDA** é suficiente e mais simples de manter.

**Quando migrar para TensorRT/Triton?**
1.  Quando a latência de classificação começar a atrapalhar a experiência do usuário.
2.  Quando tivermos múltiplos modelos rodando (ex: um para classificar, outro para sugerir resposta).
3.  Quando precisarmos economizar VRAM (memória de vídeo) para rodar mais coisas no mesmo servidor.
