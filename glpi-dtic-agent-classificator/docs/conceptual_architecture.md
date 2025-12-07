# Arquitetura Conceitual do Sistema

Esta proposta visa criar um sistema robusto, auditável e que evolui com o tempo, superando as limitações do script simples atual.

---

## 1. O Pipeline de Classificação (Fluxo do Dado)

O processo não deve ser apenas "Ler -> Classificar". Precisamos de etapas de preparação e validação.

### Etapa 1: Ingestão e Normalização
*   **Entrada:** Título + Descrição (HTML ou Texto).
*   **Processamento:**
    *   Remover tags HTML e assinaturas de e-mail (ruído).
    *   Normalizar termos (ex: "m365", "o365", "office" -> "office_365").
    *   Concatenação inteligente: `Título: {titulo} | Descrição: {resumo_descricao}`.

### Etapa 2: Recuperação Híbrida (Hybrid Retrieval)
Não confie apenas em embeddings.
*   **Caminho A (Léxico/Regras):** O ticket contém palavras-chave proibitivas ou exclusivas? (Ex: "demissão" -> RH).
*   **Caminho B (Semântico/Embedding):** Qual categoria tem o vetor mais próximo?
*   **Fusão:** Se Caminho A tiver certeza, ele ganha. Se não, usa Caminho B.

### Etapa 3: Decisão e Confiança
*   O modelo gera um Score (0-1).
*   Aplicar lógica de **Threshold Dinâmico**:
    *   Categorias críticas (Segurança) podem exigir 95% de confiança.
    *   Categorias triviais (Dúvida) podem aceitar 75%.
*   **Saída:** Categoria Sugerida + Nível de Confiança (Alto/Médio/Baixo).

### Etapa 4: Ação no GLPI
*   **Confiança Alta:** Atualiza o ticket automaticamente. Adiciona tag "Bot-Classified".
*   **Confiança Média:** Adiciona comentário privado (Follow-up) sugerindo a categoria para o técnico.
*   **Confiança Baixa:** Não faz nada (ou marca como "A Classificar").

---

## 2. Ciclo de Feedback e Aprendizado (Human-in-the-loop)

O sistema não pode ser estático. Ele precisa aprender com os erros.

### A. Coleta de Feedback
*   Monitorar tickets onde:
    *   O Bot classificou como X.
    *   O Humano mudou para Y.
*   Isso é um **exemplo de erro valioso**. Salve esse par (Ticket, X, Y) em um banco de "Casos Difíceis".

### B. Re-treino / Atualização de Referência
*   Periodicamente (ex: mensalmente):
    1.  Pegue os novos tickets resolvidos e validados.
    2.  Adicione-os ao banco de exemplos ("Golden Set").
    3.  Regere os embeddings de referência das categorias (média ponderada).
    4.  Isso faz o sistema aprender novas gírias ou problemas que surgiram no mês.

---

## 3. Governança e Configuração

Para evitar depender de desenvolvedores para ajustar regras de negócio:

### Arquivo de Configuração de Negócio (`rules.yaml` ou JSON)
Permita que um analista edite:
1.  **Lista de Categorias Ativas:** IDs e Nomes.
2.  **Descrição Canônica:** O texto que define a categoria para a IA.
3.  **Palavras-Chave de Força:** Termos que "puxam" a classificação.
4.  **Thresholds:** Nível de confiança mínimo global ou por categoria.

### Exemplo de Configuração:
```yaml
categories:
  - id: 10
    name: "Impressora"
    description: "Problemas físicos de impressão e suprimentos."
    keywords: ["toner", "papel", "atolamento"]
    threshold: 0.85

  - id: 20
    name: "Acesso VPN"
    description: "Erros de conexão remota e VPN."
    keywords: ["vpn", "forticlient", "túnel"]
    threshold: 0.90
```

---

## 4. Diagrama de Integração

```mermaid
graph TD
    User[Usuário] -->|Abre Ticket| GLPI
    GLPI -->|Webhook/Cron| Agent[Agente de Classificação]
    
    subgraph "Cérebro do Agente"
        Pre[Normalização Texto]
        Emb[Gerador Embedding (GPU)]
        Rules[Motor de Regras]
        DB[(Vetores de Categoria)]
    end
    
    Agent --> Pre
    Pre --> Emb
    Emb -->|Vetor Ticket| Rules
    DB -->|Vetores Ref| Rules
    
    Rules -->|Decisão + Confiança| Action{Confiança?}
    
    Action -->|Alta| Update[Atualiza Categoria GLPI]
    Action -->|Média| Suggest[Comenta Sugestão]
    Action -->|Baixa| Log[Loga para Análise]
    
    Update --> GLPI
    Suggest --> GLPI
```
