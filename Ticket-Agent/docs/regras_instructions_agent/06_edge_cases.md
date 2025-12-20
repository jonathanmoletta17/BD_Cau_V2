# Documentação de Casos de Borda e Testes de Integração GLPI

Esta documentação descreve os cenários de teste "Edge Cases" gerados para validar a robustez da integração com o GLPI, cobrindo limites de dados, segurança e performance.

## 1. Visão Geral
O objetivo é garantir que o Ticket Agent possa lidar com entradas extremas e erros da API do GLPI sem falhar catastroficamente, e verificar o comportamento do GLPI sob condições de estresse.

**Ambiente de Execução:** GLPI TEST (Write Access)
**Script de Geração:** `scripts/generate_edge_cases.ts`
**Script de Execução:** `src/tests/glpi_integration.ts`
**Fonte de Dados:** `data/edge_cases.json`

## 2. Cenários de Teste (Edge Cases)

Os seguintes cenários são gerados automaticamente baseados nos dados coletados do ambiente PROD (para garantir IDs válidos quando necessário):

### 2.1. Limites de Caracteres (Título)
- **Cenário:** Título com 255 caracteres (limite comum de BD).
- **Objetivo:** Verificar se o sistema aceita o limite máximo sem truncar ou erro.
- **Resultado Esperado:** Sucesso.

### 2.2. Excesso de Limites (Título)
- **Cenário:** Título com 300 caracteres.
- **Objetivo:** Verificar comportamento de truncamento ou rejeição.
- **Resultado Esperado:** Erro 400 ou Truncamento (depende da config do GLPI).

### 2.3. Payload Gigante (Content)
- **Cenário:** Descrição com ~60KB de texto (Lorem Ipsum).
- **Objetivo:** Testar limites de POST body e timeout de processamento.
- **Resultado Esperado:** Sucesso (GLPI suporta TEXT/LONGTEXT).

### 2.4. Caracteres Especiais e Injeção
- **Cenário:** Título/Conteúdo contendo `' OR 1=1; --`, tags `<script>`, emojis e caracteres unicode.
- **Objetivo:** Validar sanitização e encoding (UTF-8).
- **Resultado Esperado:** O ticket deve ser criado com o texto literal, sem executar scripts ou quebrar SQL.

### 2.5. Categoria Válida (Random)
- **Cenário:** Atribuição de uma categoria ITIL existente (coletada de PROD).
- **Objetivo:** Validar fluxo normal de classificação.
- **Resultado Esperado:** Sucesso.

### 2.6. Categoria Inválida
- **Cenário:** Atribuição de ID de categoria inexistente (ex: 999999).
- **Objetivo:** Validar tratamento de erro de chave estrangeira/validação.
- **Resultado Esperado:** Erro da API (400/404) ou criação no Root Entity (fallback).

### 2.7. Urgência Máxima
- **Cenário:** Urgência nível 5.
- **Objetivo:** Validar mapeamento de SLA.
- **Resultado Esperado:** Sucesso.

## 3. Execução e Diagnóstico

Para executar os testes:
```bash
npx tsx src/tests/glpi_integration.ts
```

### Problemas Conhecidos
- **Erro de App-Token:** Atualmente o ambiente TEST retorna `ERROR_WRONG_APP_TOKEN_PARAMETER`. Verifique `src/config/glpi_credentials.ts`.
