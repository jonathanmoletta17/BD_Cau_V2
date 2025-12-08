# Proposta de Estrutura Ideal para Contexto (JSON)

Atualmente, o arquivo `agent/category_context.json` é um dicionário simples (Chave: Valor). Para tornar o agente mais "inteligente" e controlável, proponho uma estrutura baseada em objetos detalhados.

Esta estrutura permite combinar a força da IA (descrição semântica) com a precisão de regras (palavras-chave).

---

## 1. Estrutura Proposta

O JSON deve ser uma lista de objetos ou um dicionário onde a chave é o NOME DA CATEGORIA. Cada objeto terá os seguintes campos:

*   `id` (int, opcional): O ID numérico no GLPI. Ajuda na validação.
*   `description` (string): Texto descritivo usado pela IA para entender o *conceito*.
*   `keywords` (lista de strings): Termos que, se presentes, aumentam muito a chance dessa categoria.
*   `negative_keywords` (lista de strings): Termos que, se presentes, *proíbem* essa categoria (filtros de exclusão).
*   `priority` (int): Peso para desempate (ex: categoria específica ganha de genérica).

---

## 2. Exemplos Modelo

Abaixo, veja como ficariam algumas categorias reais do seu ambiente nesta nova estrutura.

```json
{
  "TÚNEL PROCERGS": {
    "id": 11,
    "description": "Problemas de conexão VPN, acesso remoto seguro ou túnel criptografado com a rede da Procergs. Inclui erros de acesso negado ao tentar conectar.",
    "keywords": [
      "túnel",
      "tunnel",
      "vpn",
      "procergs",
      "acesso remoto"
    ],
    "negative_keywords": [
      "físico",
      "cabo de rede",
      "wi-fi"
    ],
    "priority": 10
  },

  "IMPRESSORA": {
    "id": 14,
    "description": "Suporte a dispositivos de impressão, troca de suprimentos (toner, cartucho), instalação de drivers de impressão e atolamento de papel.",
    "keywords": [
      "impressora",
      "imprimir",
      "toner",
      "cartucho",
      "papel atolado",
      "scanear"
    ],
    "negative_keywords": [
      "impressão de etiqueta",
      "crachá"
    ],
    "priority": 10
  },

  "CAIXA COMPARTILHADA": {
    "id": 4,
    "description": "Solicitações envolvendo caixas de e-mail departamentais ou de grupos, onde múltiplas pessoas têm acesso. Inclui criação e permissão de acesso.",
    "keywords": [
      "caixa compartilhada",
      "email do setor",
      "e-mail do departamento",
      "inclusão na caixa"
    ],
    "negative_keywords": [
      "meu email",
      "minha senha",
      "pessoal"
    ],
    "priority": 20
  },

  "OFFICE 365": {
    "id": 20,
    "description": "Problemas gerais com a suíte Microsoft Office, licenças, instalação do pacote Office, Teams, OneDrive e Outlook.",
    "keywords": [
      "office",
      "365",
      "word",
      "excel",
      "teams",
      "onedrive",
      "licença"
    ],
    "negative_keywords": [],
    "priority": 5
  }
}
```

---

## 3. Lógica por trás da Estrutura

### Por que `keywords` e `description` juntos?
A IA é ótima para entender "Meu computador não imprime nada", mesmo sem a palavra "impressora" (ela entende o conceito de imprimir).
Porém, a IA pode se confundir com "Preciso de acesso à pasta *Impressos*".
As `keywords` agem como âncoras: se o usuário escreveu "Túnel Procergs", quase certeza que é a categoria TÚNEL, não importa o resto do texto.

### Por que `negative_keywords`?
Ajuda a evitar falsos positivos.
Exemplo: Alguém pede "Instalação de Office" e escreve "Não é na impressora". A palavra "impressora" poderia confundir a IA, mas se estiver no contexto negativo, o agente sabe ignorar.

### Por que `priority`?
Resolve conflitos.
Se um ticket fala "Erro no Outlook da Caixa Compartilhada", ele pode parecer tanto `OFFICE 365` quanto `CAIXA COMPARTILHADA`.
Se definirmos prioridade 20 para `CAIXA COMPARTILHADA` e 5 para `OFFICE 365`, o agente escolherá a mais específica (Caixa Compartilhada).

---

## 4. Próximos Passos (Evolução)

Quando você decidir alterar o código, o script `agent/simple_agent.py` precisará ser atualizado para ler este novo formato JSON. A lógica seria algo como:

1.  Carregar JSON.
2.  Para cada ticket:
    *   Verificar `negative_keywords` (se bater, descarta categoria).
    *   Verificar `keywords` (se bater, dá bônus na pontuação).
    *   Calcular similaridade semântica com `description`.
    *   Somar pontuações e aplicar `priority`.
3.  Escolher a vencedora.
