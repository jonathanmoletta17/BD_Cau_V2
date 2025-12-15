# Necessidades Reais de Negócio - Diretoria DTIC

Este documento mapeia as demandas de gestão reais, inferidas a partir dos artefatos de software desenvolvidos e implantados no ambiente da DTIC.

## 1. Necessidades Explícitas (Evidenciadas por Soluções)

As seguintes necessidades geraram projetos específicos de software, comprovando sua prioridade para a gestão:

| Necessidade de Negócio | Solução Implementada | Resumo da Demanda |
| :--- | :--- | :--- |
| **Visão Unificada e Rápida** | *GLPI Data Service* | A gestão precisava de relatórios rápidos e consolidados que a interface nativa do GLPI não entregava. A solução foi criar um Data Warehouse em tempo real. |
| **Controle de Ativos (Carregadores)** | *SIS Carregadores Dashboard* | Demanda específica da gestão predial para parar de perder carregadores e saber quem está com eles. O painel Kanban responde: "Onde está o equipamento agora?". |
| **Monitoramento de Equipe** | *Ranking de Técnicos* | Gestores precisam saber quem está sobrecarregado e quem entrega mais. O widget de "Top 10" foi criado para dar essa visibilidade imediata. |
| **Alocação de Recursos** | *Ranking de Categorias* | Necessidade de entender para onde vai o esforço (ex: "Temos muitos chamados de Pintura, precisamos de mais pintores?"). |
| **Auditoria e Busca** | *Smart Search* | A busca nativa era insuficiente. A gestão precisava encontrar tickets antigos com filtros complexos (requerente + data + status) para auditoria e histórico. |
| **Garantia de Canais** | *Validador de Formulários* | Reclamações de usuários sobre o App Mobile levaram à criação de um robô que testa todos os formulários diariamente. |

## 2. Necessidades Latentes (Inferidas do Código)

A análise da arquitetura revela prioridades estratégicas implícitas:

### Segregação de "Silos" de Gestão
*   **Fato:** O sistema separa fisicamente TI (DTIC) de Predial (SIS).
*   **Necessidade:** A diretoria exige que métricas de manutenção predial não poluam as métricas de TI, e vice-versa. São tratadas como "empresas diferentes" dentro da mesma ferramenta.

### Eficiência de Atendimento (SLA)
*   **Fato:** O ETL extrai dados detalhados de SLA (`time_to_resolve`, `takeintoaccount_delay`), mas os dashboards atuais focam em volume.
*   **Oportunidade:** Há uma demanda latente para começar a cobrar tempos de atendimento, já que os dados já estão sendo coletados.

## 3. Painéis de Gestão Existentes

*   **SIS Maintenance Dashboard:** Focado na coordenação operacional predial (Backlog, Rankings).
*   **Carregadores Kanban:** Focado na gestão de patrimônio/ativos.
*   **Smart Search:** Ferramenta tática para analistas e coordenadores investigarem problemas específicos.

## 4. Conclusão para o Agente de Decisão

O agente deve ser configurado para responder prioritariamente sobre:
1.  **Gargalos Operacionais:** "Qual setor tem mais chamados parados?"
2.  **Produtividade:** "Quem são os técnicos com mais demandas?"
3.  **Tendências:** "O volume de chamados de rede está aumentando ou diminuindo?"
4.  **Ativos:** "Temos carregadores disponíveis?"
