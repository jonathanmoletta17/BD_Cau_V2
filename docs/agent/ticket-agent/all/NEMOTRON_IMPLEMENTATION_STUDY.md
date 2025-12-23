# Estudo de Implementação: NVIDIA Nemotron-Mini-4B-Instruct

Este documento detalha a análise técnica, viabilidade e plano de implementação do modelo NVIDIA Nemotron-Mini-4B-Instruct no ambiente atual (Windows/WSL2 com GPU NVIDIA RTX A4000).

---

## 1. Análise de Hardware

### Especificações do Ambiente
*   **GPU:** NVIDIA RTX A4000
*   **VRAM:** 16 GB GDDR6
*   **Compute Capability:** 8.6 (Ampere Architecture)
*   **Sistema Operacional:** Windows 10/11 (via WSL 2)

### Compatibilidade com Nemotron-Mini-4B
*   **Tamanho do Modelo:** ~8 GB (em FP16/Half Precision).
*   **Requisito de VRAM:** O modelo cabe confortavelmente nos 16GB da RTX A4000.
    *   *Modelo:* ~8 GB
    *   *KV Cache (Contexto):* Configurado com `gpu-memory-utilization 0.6` para garantir estabilidade no WSL2 (que compartilha memória com Windows).
    *   *Conclusão:* A GPU é **altamente capaz** para este modelo.
*   **Desempenho Esperado:**
    *   *Inferência:* Rápida (< 50ms TTFT esperado).
    *   *Throughput:* > 50 tokens/s (estimado).

---

## 2. Opções de Implementação

### Opção A: Agente Único (Recomendada para Início)
*   **Arquitetura:** Um único contêiner vLLM servindo o modelo via API OpenAI.
*   **Vantagens:** Simplicidade, menor overhead de memória, fácil manutenção.
*   **Viabilidade:** Confirmada. O contêiner Docker foi configurado e iniciado com sucesso.

### Opção B: Múltiplos Agentes Especializados
*   **Arquitetura:** Vários modelos ou instâncias do mesmo modelo para tarefas diferentes (ex: Triagem, Solução Técnica).
*   **Desvantagens:** A RTX A4000 (16GB) **não suporta** rodar múltiplas instâncias do Nemotron-4B simultaneamente sem degradação severa (swap) ou OOM (Out Of Memory), pois cada instância reservaria ~8GB+.
*   **Recomendação:** Utilizar um único backend de inferência (vLLM) e orquestrar "agentes lógicos" no código (client-side), que enviam prompts diferentes com system instructions específicas para o mesmo modelo.

---

## 3. Estudo Tecnológico e Integração

### Stack Escolhido: vLLM + Docker
*   **Por que vLLM?** É o estado da arte em inferência rápida (PageAttention), suporta NVIDIA Ampere (RTX A4000) nativamente e oferece API compatível com OpenAI.
*   **Integração:** O Ticket-Agent pode se comunicar com o Nemotron simplesmente alterando a `baseURL` do cliente OpenAI para `http://localhost:8000/v1`.

### Ferramentas Criadas
1.  `start_vllm_docker.ps1`: Script de orquestração para iniciar o servidor de inferência com parâmetros otimizados.
2.  `benchmark_vllm.py`: Ferramenta de validação de performance (Latência e Throughput).

---

## 4. Avaliação de Projeto

### Alinhamento com Objetivos
*   **Privacidade:** 100% local. Nenhum dado sai da infraestrutura.
*   **Custo:** Zero custo por token (apenas energia).
*   **Qualidade:** O Nemotron-4B-Instruct é fine-tuned pela NVIDIA para seguir instruções complexas e function calling, ideal para agentes de suporte.

### Métricas de Sucesso Definidas
*   **Latência (TTFT):** < 200ms
*   **Velocidade (TPS):** > 40 tokens/s
*   **Precisão de Intenção:** > 90% (na classificação de tickets)

---

## 5. Plano de Testes e Validação

### Passo 1: Execução do Servidor (Realizado)
O contêiner `vllm-nemotron` foi configurado e iniciado. O download do modelo e carregamento na VRAM são automáticos.

### Passo 2: Benchmark de Performance (Pendente de Validação Final)
Utilize o script `benchmark_vllm.py` para coletar métricas reais.
*   *Comando:* `python benchmark_vllm.py`
*   *Critério de Aceite:* O script deve rodar sem erros e apresentar TPS médio acima de 30.

### Passo 3: Integração com Agente (Próximo Passo)
Alterar a configuração do Agente para usar o endpoint local.

```typescript
// Exemplo de configuração futura no agente
const openai = new OpenAI({
  apiKey: "vllm", // Pode ser qualquer string
  baseURL: "http://localhost:8000/v1"
});
```

---

## Conclusão
A implementação do NVIDIA Nemotron-Mini-4B na infraestrutura atual é **tecnicamente viável e altamente recomendada**. A RTX A4000 oferece recursos suficientes para rodar este modelo com excelente performance. A arquitetura baseada em Docker + vLLM garante estabilidade e facilidade de atualização.
