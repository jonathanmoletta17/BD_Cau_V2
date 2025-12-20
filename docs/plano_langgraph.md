Segue o **plano reescrito, consolidado e organizado**, pronto para você **enviar diretamente a outro modelo** para que ele **crie o projeto do zero**, sem ambiguidade e sem abstração excessiva.

---

# Plano de Criação — Agente de Triagem Local com LLM

**Setup mínimo absoluto (≤ 30 minutos)**

## Objetivo do Projeto

Construir um **agente de triagem de TI simples**, totalmente **local**, com **controle determinístico de fluxo**, usando **LLM apenas para compreensão de texto**.

**Restrições obrigatórias:**

* Tudo rodando localmente
* Nenhuma API paga
* Um único fluxo de triagem inicial
* Arquitetura simples, didática e extensível
* Não é um chatbot genérico

---

## Stack Técnica

* Modelo local via Ollama
* Python
* LangChain (interface com o modelo)
* LangGraph (controle de fluxo/estado)

---

## Passo 1 — Modelo Local (≈ 5 minutos)

Verificar se o modelo local está funcional.

Teste obrigatório:

* Executar o modelo local (llama 3.1)
* Confirmar que responde a um prompt simples

Se respondeu, o ambiente de modelo está OK.

---

## Passo 2 — Ambiente Python (≈ 5 minutos)

Criar ambiente virtual e instalar dependências mínimas.

Dependências necessárias:

* langchain
* langgraph
* langchain-community
* ollama (cliente Python)

Não instalar nada além disso.

---

## Passo 3 — Conceito Central do Sistema (Fundamental)

### O que será construído

Um **fluxo de decisão**, não um chatbot conversacional.

O sistema é composto **exatamente** por quatro partes fixas:

1. **Estado da conversa** (memória estruturada)
2. **Classificador de intenção**
3. **Extrator de dados (entidades)**
4. **Controlador de fluxo**

LangChain e LangGraph são usados **apenas para organizar essas partes**, não para tomar decisões de negócio.

---

## 1. Estado da Conversa (Elemento Central)

O estado representa uma **ficha de atendimento**, nunca texto livre.

Exemplo de estado inicial:

* Intenção: vazia
* Sistema: vazio
* Ação: vazia
* Usuário: vazio
* Completo: não

Características:

* Apenas dados estruturados
* Vive durante toda a conversa
* Nunca depende de “memória textual” do modelo

---

## 2. Processamento da Primeira Mensagem

Exemplo de entrada do usuário:

> “Preciso liberar acesso ao SOE pro João”

Regra fundamental:

* O sistema **não responde imediatamente ao usuário**

Antes de qualquer resposta, três etapas internas são executadas.

---

## 3. Classificação de Intenção

O modelo recebe **uma pergunta objetiva**, por exemplo:

* “Classifique a intenção: acesso, hardware, criação de usuário ou outro.”

Resposta esperada do modelo:

* ACCESS

Apenas isso.

A intenção é salva no estado:

* Intenção = ACCESS

Nenhuma pergunta ao usuário ocorre nessa etapa.

---

## 4. Extração de Dados (Entidades)

Em seguida, o modelo recebe **outra tarefa**, separada da classificação:

* “Extraia qualquer informação relevante para um pedido de acesso.”

Resposta esperada (estruturada):

* Sistema: SOE
* Ação: liberar
* Usuário: João

Regras:

* O sistema só preenche campos que vierem explícitos
* Nada é inferido ou inventado

Estado após extração:

* Intenção: ACCESS
* Sistema: SOE
* Ação: liberar
* Usuário: João

---

## 5. Controle de Fluxo (Responsabilidade do LangGraph)

O LangGraph avalia o estado com **regras determinísticas**, por exemplo:

* Tem intenção?
* Tem sistema?
* Tem ação?
* Tem usuário?

Se todos os campos obrigatórios estiverem preenchidos:

* O fluxo é considerado completo

O modelo **não decide isso**.

---

## 6. Resposta ao Usuário (Somente no Final)

Somente após o estado estar completo, o sistema responde:

> “Perfeito. Vou abrir o chamado de liberação de acesso ao SOE para o João.”

Características dessa resposta:

* Não repete informações
* Não confirma o óbvio
* Não faz perguntas redundantes

---

## Exemplo de Fluxo Incompleto (Hardware)

Entrada do usuário:

> “Meu computador não liga”

Processamento interno:

* Intenção: HARDWARE
* Equipamento: computador
* Problema: não liga

Estado:

* Intenção: HARDWARE
* Equipamento: computador
* Problema: não liga
* Localização: vazia

O controlador de fluxo detecta campos obrigatórios faltantes.

Somente então o sistema pergunta:

> “Em qual setor o equipamento está localizado?”

Regra crítica:

* O modelo apenas formula a frase
* Ele **não decide** o que perguntar

---

## Papel Real do LangGraph

LangGraph é responsável por:

* Definir qual pergunta vem agora
* Impedir perguntas repetidas
* Decidir quando finalizar
* Resetar o fluxo se necessário

O modelo **não pode**:

* Escolher a próxima pergunta
* Ignorar regras de negócio
* Repetir campos já preenchidos
* Conduzir o processo

---

## O Que Este Projeto NÃO É

* Não é um chatbot genérico
* Não usa prompt gigante
* Não depende de “bom senso” do modelo
* Não mistura conversa com lógica de negócio

---

## Por Que Essa Arquitetura Funciona

* LLM: compreensão de linguagem natural
* Código/LangGraph: disciplina de processo

Cada parte faz **apenas o que sabe fazer bem**.

---

## Escopo do MVP Inicial

Para a primeira implementação:

* Apenas **um fluxo** (ex: HARDWARE)
* Apenas **3 campos obrigatórios**
* Sem integração com GLPI
* Tudo rodando localmente
* Foco total em clareza e controle

---

**Objetivo final deste pedido:**
Criar a estrutura mínima funcional desse agente, pronta para evolução futura, respeitando rigorosamente este plano.
