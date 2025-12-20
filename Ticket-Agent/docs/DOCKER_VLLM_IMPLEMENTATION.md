# Guia de Implementação e Otimização: vLLM via Docker (NVIDIA Nemotron)

Este documento detalha o processo para configurar, executar e otimizar o modelo **NVIDIA Nemotron-Mini-4B-Instruct** (e variantes) usando Docker e vLLM em um ambiente Windows com GPU NVIDIA RTX A4000.

---

## 1. Pré-requisitos e Configuração do Ambiente

Para rodar contêineres Docker com aceleração de GPU no Windows, utilizamos o **WSL 2** (Windows Subsystem for Linux) como backend.

### 1.1. Verificação de Drivers NVIDIA
No Windows (Host), certifique-se de que possui o driver NVIDIA mais recente instalado.
*   **Comando de verificação (PowerShell):** `nvidia-smi`
*   **Requisito:** Driver versão 535.xx ou superior recomendado para suporte completo ao CUDA 12.x.

### 1.2. Docker Desktop com WSL 2
1.  Instale o **Docker Desktop for Windows**.
2.  Nas configurações do Docker (`Settings` > `General`), marque: `Use the WSL 2 based engine`.
3.  Nas configurações de `Resources` > `WSL Integration`, certifique-se de que a integração está habilitada para sua distribuição Linux padrão (ex: Ubuntu).
4.  **GPU Support:** O Docker Desktop moderno já configura automaticamente o passthrough da GPU para o WSL 2. Não é necessário instalar o `nvidia-container-toolkit` manualmente dentro do WSL se estiver usando o Docker Desktop atualizado.

---

## 2. Implementação do vLLM

Utilizaremos a imagem oficial `vllm/vllm-openai`, que fornece um servidor compatível com a API da OpenAI.

### 2.1. Script de Inicialização (PowerShell)
Crie um arquivo chamado `start_vllm_docker.ps1` na raiz do projeto para facilitar a execução com os parâmetros corretos.

**Parâmetros Otimizados para RTX A4000 (16GB):**
*   `--model`: `nvidia/Nemotron-Mini-4B-Instruct`
*   `--gpu-memory-utilization`: `0.9` (Reserva 90% da VRAM para o modelo e KV Cache. Como o modelo 4B é pequeno (~8GB em FP16), isso deixa ~6GB para contexto, o que é excelente).
*   `--max-model-len`: `4096` (Ou mais, dependendo do uso. O modelo suporta mais, mas 4096 é seguro para começar e garante performance).
*   `--dtype`: `half` (FP16 para melhor performance sem perda significativa de qualidade vs FP32).

### 2.2. Comando Docker
```powershell
# Exemplo de comando (será salvo no script start_vllm_docker.ps1)
docker run --runtime nvidia --gpus all `
    -v "$HOME/.cache/huggingface:/root/.cache/huggingface" `
    --env "HUGGING_FACE_HUB_TOKEN=seu_token_aqui" `
    -p 8000:8000 `
    --ipc=host `
    vllm/vllm-openai:latest `
    --model nvidia/Nemotron-Mini-4B-Instruct `
    --trust-remote-code `
    --dtype half `
    --gpu-memory-utilization 0.9 `
    --max-model-len 4096
```

---

## 3. Testes de Capacidade e Benchmark

Para validar a implementação, criaremos um script Python dedicado que estressa o servidor e mede métricas chave.

### 3.1. Métricas Definidas
*   **TTFT (Time To First Token):** Latência inicial. Quanto tempo demora para o primeiro caractere aparecer. Ideal < 200ms.
*   **TPS (Tokens Per Second):** Velocidade de geração. Ideal > 50 tokens/s para sensação de "instantâneo".
*   **Latência Total:** Tempo total da requisição.

### 3.2. Cenários de Teste
1.  **Chat Curto (Ping):** "Olá, quem é você?" (Valida latência mínima).
2.  **Raciocínio (Carga Média):** "Explique como funciona o DNS em detalhes." (Valida throughput de geração).
3.  **Function Calling (Específico Nemotron):** Enviar prompt de ferramenta para validar formato JSON.

---

## 4. Guia de Troubleshooting

### Erro: "CUDA out of memory"
*   **Causa:** O modelo + KV Cache excedeu 16GB.
*   **Solução:** Reduza `--gpu-memory-utilization` para `0.8` ou reduza `--max-model-len` para `2048`.

### Erro: "Model not found" ou Erro de Download
*   **Causa:** Token do Hugging Face inválido ou falta de permissão no repositório do modelo.
*   **Solução:** Verifique se aceitou os termos de uso do modelo no site do Hugging Face e se o token (HF_TOKEN) está correto no script.

### Performance Baixa (TPS < 20)
*   **Causa:** Docker pode estar rodando via Hyper-V em vez de WSL 2, ou a GPU não está sendo usada.
*   **Solução:** Verifique os logs do container (`docker logs <container_id>`) logo no início. Deve aparecer logs sobre detecção de GPU (ex: `Requires CUDA version...`). Se aparecer "CPU", a configuração do Docker está errada.

---

## 5. Próximos Passos
1.  Obtenha seu **Hugging Face Token** (com permissão de leitura).
2.  Execute `start_vllm_docker.ps1`.
3.  Aguarde o servidor iniciar (logs dirão `Uvicorn running on http://0.0.0.0:8000`).
4.  Execute `python benchmark_vllm.py` para validar.
