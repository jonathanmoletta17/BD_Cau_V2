# Catálogo de Formulários e Campos (GLPI)

Este documento consolida os formulários detectados nos tickets com “Dados do formulário” e lista seus campos característicos, com exemplos resumidos sem dados sensíveis.

## Método de Coleta
- Fonte: descrições dos tickets contendo “Dados do formulário”.
- Extração: parsing de linhas do tipo `n) CAMPO : valor` e `CAMPO : valor`.
- Foco: identificação de campos por formulário e exemplos de estrutura.

## Acesso a Sistemas – Rede Piratini
- Campos
  - TIPO
  - ORGANIZAÇÂO
  - SETOR
  - NOME COMPLETO
  - ID FUNCIONAL
  - CARGO
  - CPF
  - SERVIDOR RESPONSÁVEL (Para Estagiário[a])
  - DESCRIÇÃO
  - RAMAL
  - HOSTNAME
- Exemplo resumido
  - “TIPO: NOVO USUÁRIO; ORGANIZAÇÂO: [órgão]; SETOR: [unidade]; NOME COMPLETO; ID FUNCIONAL; CPF; RAMAL; HOSTNAME; DESCRIÇÃO”

## Office 365 – EXCLUSÃO / NOVA CONTA / PERMISSÕES
- Campos (quando estruturado em formulário)
  - Este atendimento é para quem?
  - Qual o nome desta pessoa?
  - Localização
  - Telefone de Contato
  - Tipo de Serviço (EXCLUSÃO, NOVA CONTA DE EMAIL, PERMISSÃO PARA CRIAR EQUIPES, etc.)
  - Descrição
  - EMAIL DO USUÁRIO
  - NOME COMPLETO
  - MATRÍCULA/IDENTIFICAÇÃO
  - CPF
  - SETOR
  - CARGO
- Exemplo resumido
  - “Tipo de Serviço: NOVA CONTA DE EMAIL; EMAIL DO USUÁRIO: [usuario@]; Localização; Telefone; Nome completo; Setor; Cargo; Descrição”

## Outlook – Caixa Compartilhada
- Campos
  - Localização
  - Telefone de Contato / Ramal
  - Descrição (solicitação de adicionar/excluir usuários)
  - Identificação da caixa/unidade (aparece em texto)
  - Lista de usuários (e-mails) e tipo de acesso (ler/enviar/gerenciar)
- Exemplo resumido
  - “Adicionar usuário à caixa compartilhada [unidade/caixa]; Localização; Ramal; Descrição com lista de usuários e tipo de acesso”

## Atendimento ao Usuário – Suporte (Genérico)
- Campos
  - LOCALIZAÇÃO
  - RAMAL
  - DESCRIÇÃO DO PEDIDO
  - ARQUIVO
  - HOSTNAME
- Exemplo resumido
  - “LOCALIZAÇÃO: [endereço/unidade]; RAMAL: [xxxx]; DESCRIÇÃO DO PEDIDO; HOSTNAME: [ws-…]”

## WIFI (variação dentro de Acesso a Sistemas)
- Campos
  - TIPO (WIFI)
  - ORGANIZAÇÂO
  - SETOR
  - DESCRIÇÃO
  - RAMAL
  - HOSTNAME
- Exemplo resumido
  - “TIPO: WIFI; ORGANIZAÇÂO: [órgão]; SETOR: [unidade]; DESCRIÇÃO; RAMAL; HOSTNAME”

## Ingresso – Anexo de Arquivo do RHE
- Campos
  - TIPO (INGRESSO – ANEXO DE ARQUIVO DO RHE)
  - NOME COMPLETO
  - ORGANIZAÇÂO
  - SETOR
  - CARGO
  - ENVIAR ARQUIVO COM OS DADOS DE NOVO USUÁRIO
- Exemplo resumido
  - “TIPO: INGRESSO – ANEXO DE ARQUIVO DO RHE; Nome completo; Organização; Setor; Cargo; Documento anexado”

## Observações Importantes
- Campos sensíveis (ex.: CPF) surgem em solicitações de criação/alteração de acesso. Devem ser solicitados apenas quando estritamente necessários e tratados com cautela.
- Em alguns casos (Office/Outlook), detalhes aparecem em texto livre sem o padrão numerado; ainda assim, os campos acima são recorrentes e úteis para o agente.


