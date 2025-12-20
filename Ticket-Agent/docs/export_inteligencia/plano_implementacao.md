# Plano de Implementação (Roadmap de Migração)

## Fase 1: Preparação e Exportação (Dia 1-2)
- [ ] **Empacotamento**: Copiar os arquivos Core (`llm_service.py`, `classifier_service.py`, `models/`) para a estrutura do novo projeto.
- [ ] **Setup de Ambiente**: Configurar o servidor Ollama acessível pelo novo agente.
- [ ] **Transferência de Conhecimento**: Copiar `categories_list.json` e `prompts.json` atuais para garantir baseline idêntico.

## Fase 2: Adaptação e Integração (Dia 3-5)
- [ ] **Refatoração de Config**: Alterar `src/config.py` ou equivalentes para usar o gerenciador de configuração do novo projeto.
- [ ] **Injeção de Dependência**: Instanciar `LLMService` e `ClassifierService` dentro do container de serviços do novo agente.
- [ ] **Ajuste de Caminhos**: Configurar o `ClassifierService` para ler o JSON de categorias do local correto na nova estrutura.

## Fase 3: Validação Funcional (Dia 6)
- [ ] **Smoke Test**: Rodar script simples de "Hello World" (enviar "Meu mouse quebrou" e verificar se classifica).
- [ ] **Teste de Carga**: Disparar 10 requisições simultâneas para validar estabilidade do conector HTTP.

## Fase 4: Otimização (Dia 7+)
- [ ] **Implementar Retry**: Adicionar lógica de retentativa em caso de falha de JSON.
- [ ] **Refinamento de Prompts**: Ajustar `prompts.json` se o novo agente tiver uma "persona" diferente.

## Métricas de Sucesso
1.  **Taxa de Erro**: < 5% de falhas técnicas (timeout/json error).
2.  **Acurácia**: Manter a mesma acurácia do agente original (> 90% em testes de regressão).
3.  **Tempo de Resposta**: Médio < 5s (assumindo hardware igual).

## Protocolo de Validação
Para cada funcionalidade migrada, executar:
1.  Input: "Preciso de acesso ao SAP"
2.  Esperado: Categoria "Acesso > SAP" (ou similar), Tipo "Requisição".
3.  Critério de Aceite: JSON de resposta válido e ID de categoria > 0.
