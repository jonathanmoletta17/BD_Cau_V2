# Contexto Técnico do Projeto BD_Cau_V2

**Última Atualização**: 2025-12-19
**Foco Atual**: Governança, Ticket Agent e NVIDIA NIM.

---

## 🎯 Objetivo Principal
Desenvolver e manter um ecossistema de agentes inteligentes para automação de suporte de TI (GLPI), operando sob estritos protocolos de governança e segurança.

## 🏗️ Estrutura Ativa (Onde trabalhamos)
*   **`agents/Ticket-Agent/`**: O coração da automação atual.
    *   Stack: TypeScript, Node.js, Docker.
    *   Responsabilidade: Interagir com GLPI, triagem de tickets, uso de LLM para estruturação.
*   **`.antigravity/`**: Memória e contexto do agente.
*   **`local-ai-stack/`**: Infraestrutura Docker para NVIDIA NIM e serviços de IA locais.

## 🚫 Legacy / Deprecated (Ignorar)
*   `glpi-data-service-v2` (Morto)
*   `rag-local` (Descontinuado)
*   Referências a "Llama 3 via Ollama" como motor principal (O foco migrou para NVIDIA NIM/Nemotron).

---

## �️ Stack Tecnológica Atualizada

### IA & Infraestrutura
- **Motor de Inferência**: NVIDIA NIM (Dockerizados).
- **Modelos**: Nemotron-Mini-4B (Rápido/Edge), Llama 3 (Raciocínio complexo se necessário).
- **Hardware**: NVIDIA RTX A4000 (16GB VRAM).
    - *Regra*: Respeite os limites de VRAM. Não suba múltiplos modelos pesados simultaneamente.

### Backend & Agentes
- **Linguagem**: TypeScript (Preferencial para novos agentes), Python (Scripts de análise/IA).
- **Integração GLPI**: Via REST API segura.

---

## � Protocolo Operacional (Vibe Code)

1.  **Estudo**: Entenda o problema lendo logs e código.
2.  **Plano**: Escreva `implementation_plan.md`.
3.  **Aprovação**: Espere o "OK" do usuário.
4.  **Execução**: Implemente cirurgicamente.
5.  **Prova**: Valide e mostre logs de sucesso.

**Se este arquivo entrar em conflito com `.cursorrules`, o `.cursorrules` tem precedência.**
