# Segurança, Privacidade e Escopo de Acesso

Análise de riscos e controles de segurança para o Agente de Dados do GLPI.

## 1. Escopo de Acesso (Visibilidade)

O agente opera com **permissões espelhadas** do usuário de serviço configurado na API do GLPI.

*   **Autenticação:** O sistema utiliza `App-Token` (identificação da aplicação) + `User-Token` (credencial de serviço).
*   **Visão de Dados:** O agente enxerga **tudo** que o usuário do token enxerga. Não há filtros de linha (Row-Level Security) no código de extração. Se o token for de Admin, o banco analítico conterá dados de Admin.
*   **Segregação DTIC vs. SIS:**
    *   Implementada fisicamente via schemas de banco de dados (`dtic` e `sis`).
    *   Garante que dados de TI não se misturem com dados de Manutenção Predial.
    *   **Risco:** Um desenvolvedor com acesso ao banco `glpi_data` tem acesso a ambos os schemas se for superusuário do Postgres.

## 2. Dados Sensíveis Identificados

O banco de dados analítico contém réplicas fiéis do GLPI, incluindo campos de texto livre que apresentam alto risco de vazamento de dados pessoais (PII).

| Tabela/Campo | Classificação | Risco / Detalhe |
| :--- | :--- | :--- |
| `tickets.descricao` | **Alta Criticidade** | Texto livre (HTML). Frequentemente contém nomes, CPFs, telefones, e-mails e senhas coladas por usuários. |
| `tickets.titulo` | Média Criticidade | Pode conter nomes de pessoas ou resumos de incidentes sigilosos. |
| `tickets.requerente` | Dado Pessoal | Nome completo do cidadão ou servidor. |
| `tickets.tecnico` | Dado Pessoal | Nome completo do servidor público (monitoramento de desempenho). |
| `tickets.localizacao` | Dado Reservado | Pode revelar rotinas ou localização exata de autoridades ou equipamentos críticos. |

## 3. Controles Existentes e Limitações

### O que JÁ EXISTE:
*   **Sanitização de XSS:** O conversor `_html_to_markdown` remove scripts maliciosos da descrição, protegendo quem visualiza os dados em dashboards web.
*   **Logs de Sistema:** Tabelas `sync_history` registram operações de carga, permitindo auditar quando os dados foram extraídos.
*   **Sessões Efêmeras:** O cliente API encerra a sessão (`killSession`) imediatamente após o uso, reduzindo janela de ataque.

### O que NÃO EXISTE (Limitações Críticas):
*   **Sem Anonimização:** O script de ETL **copia os dados na íntegra**. Não há mascaramento de CPF ou nomes.
*   **Sem Auditoria de Leitura:** Não há logs de "quem consultou o dashboard".
*   **Sem Controle de Acesso Granular:** Quem tem acesso ao banco analítico vê todos os tickets do schema.

## 4. Recomendações para a Diretoria

1.  **Restrição de Acesso:** O acesso ao banco de dados do Agente deve ser tão restrito quanto o acesso de Super-Admin ao GLPI.
2.  **Relatórios Seguros:** Evitar expor o campo `descricao` em relatórios abertos. Usar apenas para análise quantitativa ou qualitativa por IAs em ambiente seguro.
3.  **Token Dedicado:** Garantir que o `User-Token` usado na integração tenha permissões de "Somente Leitura" no GLPI, se possível, para evitar edições acidentais (embora o código atual faça apenas leitura).
