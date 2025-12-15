# AI Engineer Framework: Manual para Antigravity
> **"Do Probabilístico ao Determinístico"**

Este documento introduz o **Universal AI Framework**, uma infraestrutura criada para eliminar erros de alucinação e falhas de integração no desenvolvimento assistido por IA.

---

## 🚨 O Problema que Resolvemos
Até hoje, o desenvolvimento com IA seguia um padrão arriscado:
1.  Pedimos código para a IA.
2.  A IA "imagina" como o banco de dados é (alucinação).
3.  A IA gera código que funciona isoladamente (Mock) mas quebra em produção.
4.  Resultado: Retrabalho, frustração e quebra de confiança.

**A Solução:** Inverter o fluxo. A IA não pode mais "imaginar"; ela deve "obedecer" a uma especificação validada contra um ambiente real.

---

## 🛠️ O Que Foi Entregue (O Kit)

Criamos uma CLI (Interface de Linha de Comando) chamada `ai-engineer` que padroniza o trabalho.

### 1. A Ferramenta (`ai.bat`)
Localizada em `_UNIVERSAL_AI_FRAMEWORK/`, esta ferramenta é o seu copiloto de governança.

#### Comandos Principais:

*   `ai check` (Pre-Flight Check)
    *   **O que faz:** Verifica se Docker, Banco de Dados, .env e Ollama estão rodando e acessíveis.
    *   **Quando usar:** Toda manhã, antes de começar a codar. Se der vermelho, não adianta pedir código para a IA.

*   `ai spec <nome_da_feature>`
    *   **O que faz:** Cria um template Markdown padronizado em `docs/specs/`.
    *   **Quando usar:** Antes de escrever qualquer linha de código.
    *   **Por que:** Obriga o desenvolvedor a definir Entradas, Saídas e Regras de Negócio antes da IA tentar adivinhar.

*   `ai init`
    *   **O que faz:** Instala a estrutura de pastas em novos projetos.

---

## 🚀 Fluxo de Trabalho (O Novo Padrão)

A partir de agora, qualquer desenvolvedor (Humano ou IA) deve seguir este ciclo:

### Passo 1: Validação de Ambiente
```powershell
./_UNIVERSAL_AI_FRAMEWORK/ai.bat check
# [OK] Database Connection: OK
# [OK] Ollama Service: OK
```
*Se falhar aqui, pare. Arrume o ambiente.*

### Passo 2: Especificação (Spec-First)
```powershell
./_UNIVERSAL_AI_FRAMEWORK/ai.bat spec analise_risco_ticket
```
Isso cria um arquivo `docs/specs/YYYYMMDD_analise_risco_ticket.md`. Preencha-o com os tipos de dados reais (ex: "O campo `id` é Integer, não String").

### Passo 3: Teste de Integração (TDD Real)
Peça para a IA:
> "Crie um teste de integração em `tests/integration/` que valide se a tabela X existe e se a coluna Y é do tipo Integer, conforme a Spec."

**Regra de Ouro:** Proibido usar Mocks para testar banco de dados. O teste deve conectar no Docker real.

### Passo 4: Implementação
Peça para a IA:
> "Implemente a feature seguindo estritamente a Spec em `docs/specs/...`. Use Pydantic para validar os dados."

---

## 🧠 Por que isso é melhor?

1.  **Fim do "Merge Error":** Como validamos o schema do banco *antes* de codar, a IA nunca mais vai tentar somar String com Integer (o erro que causou a aposta).
2.  **Documentação Viva:** As Specs não são burocracia; são o "prompt mestre" que garante que a IA não alucine.
3.  **Portabilidade:** Copie a pasta `_UNIVERSAL_AI_FRAMEWORK` para qualquer projeto Python e você tem governança imediata.

---

## 📝 Resumo para o Time

> "Não aceitamos mais código gerado por IA que não tenha sido precedido por uma Spec e validado por um Teste de Integração Real."

Este é o nosso novo alicerce.

**Assinado:** Trae AI
