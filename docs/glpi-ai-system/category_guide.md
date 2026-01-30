# Guia de Configuração de Categorias GLPI

Este guia foi elaborado a partir da análise de dados reais do ambiente de DTICUÇÃO (`glpi_data_audit.md`). Ele serve como referência para entender o que cada categoria representa na prática e como configurá-las no futuro.

---

## 1. Tabela Mestre de Categorias (DTICução)

| ID | Nome da Categoria | Caminho Completo (Hierarquia) |
|:--:|:---|:---|
| **11** | TÚNEL PROCERGS | ACESSO A SISTEMAS > TÚNEL PROCERGS |
| **13** | FPE | ACESSO A SISTEMAS > SOE > FPE |
| **17** | PROA | ACESSO A SISTEMAS > SOE > PROA |
| **22** | LIBERAÇÃO DE ACESSO | ACESSO A SISTEMAS > REDE > LIBERAÇÃO DE ACESSO |
| **2**  | EMAIL | ACESSO A SISTEMAS > OFFICE 365 > EMAIL |
| **4**  | CAIXA COMPARTILHADA | ACESSO A SISTEMAS > OFFICE 365 > EMAIL > CAIXA COMPARTILHADA |
| **14** | IMPRESSORA | IMPRESSORA |
| **25** | INSTALAÇÃO DE EQUIPAMENTOS | AJUDA E SUPORTE > INSTALAÇÃO DE EQUIPAMENTOS |
| **8**  | INSTALAÇÃO DE SOFTWARE | AJUDA E SUPORTE > INSTALAÇÃO DE SOFTWARE |
| **7**  | AJUDA E SUPORTE | AJUDA E SUPORTE |
| **18** | INFRAESTRUTURA | DTIC > INFRAESTRUTURA |

*(Lista resumida com as categorias mais ativas encontradas na auditoria)*

---

## 2. Definições e Exemplos Práticos

Abaixo, detalhamos as categorias mais críticas com base no uso real.

### 🟢 TÚNEL PROCERGS (ID 11)
*   **Definição:** Problemas técnicos ou solicitações de configuração referentes à conexão VPN/Túnel com a rede da Procergs.
*   **Termos Comuns:** `túnel`, `procergs`, `vpn`, `acesso remoto`, `acesso negado`.
*   **Exemplo Típico:**
    > "Erro ao conectar no túnel, aparece mensagem de acesso negado."

### 🟢 LIBERAÇÃO DE ACESSO (ID 22)
*   **Definição:** Solicitações para conceder permissões de acesso a pastas de rede, grupos de usuários ou sistemas específicos que não têm categoria própria.
*   **Termos Comuns:** `liberação`, `acesso`, `pasta`, `rede`, `permissão`, `grupo`.
*   **Exemplo Típico:**
    > "Solicito liberar acesso da servidora Fulana à pasta compartilhada do Administrativo."

### 🟢 IMPRESSORA (ID 14)
*   **Definição:** Instalação de drivers, configuração de impressoras em rede, troca de toner ou resolução de falhas de impressão.
*   **Termos Comuns:** `impressora`, `toner`, `instalação`, `papel`, `mancha`.
*   **Exemplo Típico:**
    > "Instalação de impressora no núcleo de conservação."

### 🟢 CAIXA COMPARTILHADA (ID 4)
*   **Definição:** Criação ou inclusão de usuários em caixas de e-mail departamentais (não pessoais).
*   **Termos Comuns:** `caixa compartilhada`, `email do setor`, `inclusão`, `acesso`.
*   **Exemplo Típico:**
    > "Gostaria de adicionar a servidora à caixa de e-mail do protocolo."

### 🟢 FPE (ID 13)
*   **Definição:** Suporte específico ao sistema Finanças Públicas do Estado (FPE), incluindo perfis de acesso e erros no sistema.
*   **Termos Comuns:** `fpe`, `finanças`, `atestador`, `perfil`, `liberação de pedidos`.
*   **Exemplo Típico:**
    > "Solicito cadastramento do servidor como atestador no FPE."

### 🟢 PROA (ID 17)
*   **Definição:** Suporte ao sistema de Processos Administrativos (PROA).
*   **Termos Comuns:** `proa`, `processo`, `acesso`, `caixa`.
*   **Exemplo Típico:**
    > "Solicito acesso ao sistema PROA para a nova estagiária."

---

## 3. Como usar este guia

1.  **Para treinar humanos:** Use as definições acima para orientar a equipe de N1.
2.  **Para configurar o Agente:**
    *   Use os **Termos Comuns** para preencher o campo `keywords` no JSON de contexto.
    *   Use a **Definição** para preencher o campo `description` (que gera o embedding semântico).
    *   Use os **Exemplos** para testar se o agente está classificando corretamente.

---

## 4. Observações de Auditoria

*   **Ambiguidade:** Notei que muitos tickets de "Instalação de Office" caem tanto em `OFFICE 365` quanto em `INSTALAÇÃO DE SOFTWARE`. É preciso definir uma regra de desempate (ex: se for Office, priorizar a categoria Office).
*   **Genéricos:** A categoria `AJUDA E SUPORTE` (ID 7) está recebendo muitos tickets que poderiam ser específicos (cabos de rede, dúvidas simples). Pode ser interessante criar subcategorias ou instruir o agente a tentar evitar essa categoria "guarda-chuva" se houver uma opção melhor.
