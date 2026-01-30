# Arquitetura do Projeto de Classificação GLPI

Este documento descreve, em linguagem técnica acessível, como o sistema de classificação automática de tickets está estruturado. O objetivo é que você entenda o papel de cada componente antes de pensar em evoluções.

---

## 1. Visão Geral dos Componentes

O sistema é composto por três pilares principais:

1.  **O Conector (`glpi_agent/glpi_client.py`)**: Responsável por falar a "língua" do GLPI. Ele sabe como autenticar, como pedir dados e como enviar atualizações.
2.  **O Cérebro (`agent/simple_agent.py`)**: Responsável pela inteligência. Ele carrega modelos de IA, entende o texto do ticket e decide qual é a melhor categoria.
3.  **O Analista (`scripts/analysis/analyze_tickets.py`)**: Responsável por olhar para os dados em massa, gerar relatórios e ajudar na auditoria, sem necessariamente alterar tickets.

---

## 2. Análise Detalhada dos Scripts

### A. `glpi_agent/glpi_client.py` (O Conector)

**Resumo:**
Este arquivo é a ponte entre nosso código Python e o servidor GLPI. Ele isola toda a complexidade de rede, autenticação e tratamento de erros de API. Nenhum outro script deve "falar" com o GLPI diretamente; todos devem usar este cliente.

**Estrutura:**
*   **Imports:** Bibliotecas de rede (`urllib`), JSON e configurações.
*   **Classe `GlpiClient`:**
    *   `__init__`: Carrega configurações de ambiente (URLs, tokens).
    *   `init_session()`: Troca tokens de usuário/app por um *Session-Token* temporário.
    *   `search_items()` / `list_items_range()`: Fazem buscas (GET) com filtros.
    *   `update_ticket_category()`: Envia comando de atualização (PUT).

**Padrões e Lógica:**
1.  **Configuração via Ambiente:** O cliente decide se conecta em TESTE ou DTICUÇÃO olhando variáveis de ambiente, não código fixo (idealmente).
2.  **Sessão Persistente:** Ele obtém um token no início e o reutiliza em todas as chamadas seguintes para ser eficiente.
3.  **Tratamento de Erro:** Se o GLPI falhar (rede ou erro 500), o cliente captura e retorna `None` ou `False`, evitando que o programa todo quebre.

---

### B. `agent/simple_agent.py` (O Cérebro)

**Resumo:**
É aqui que a "mágica" da IA acontece. Este script carrega o modelo de linguagem (embeddings), lê as definições de categorias (`agent/category_context.json`) e processa os tickets um a um para classificá-los.

**Estrutura:**
*   **Inicialização:** Conecta no GLPI (via `GlpiClient`) e carrega o modelo de IA (SentenceTransformer).
*   **Carga de Contexto:** Lê o arquivo JSON com as descrições das categorias.
*   **`process_ticket(ticket)`:**
    1.  Combina Título + Conteúdo do ticket.
    2.  Gera um "embedding" (vetor numérico) para o ticket.
    3.  Compara esse vetor com os vetores das categorias (similaridade).
    4.  Se a confiança for alta (ex: > 80%), sugere a atualização.

**Padrões e Lógica:**
*   **Zero-Shot Classification:** O agente não foi "treinado" do zero; ele usa um modelo pré-treinado que entende linguagem natural e compara o *significado* do ticket com o *significado* da categoria (definido no JSON).

---

### C. `scripts/analysis/analyze_tickets.py` (O Analista)

**Resumo:**
Script utilitário focado em extração de dados e relatórios. Ele não altera tickets (geralmente), apenas lê em grandes quantidades para gerar insights, como os relatórios de auditoria que criamos.

**Estrutura:**
*   **Modos de Execução:** Pode rodar em modo simples (lista específica de URLs) ou modo `audit` (varredura geral).
*   **Funções Auxiliares:** `clean_html()` para limpar o texto sujo vindo do GLPI.
*   **Geração de Markdown:** Formata os dados brutos em tabelas legíveis para humanos.

---

## 3. Exemplos Didáticos

Para desmistificar o código, veja abaixo exemplos simplificados que capturam a essência de cada parte.

### Exemplo 1: O Conector (Mini Client)
```python
import requests

class MiniGlpi:
    def __init__(self, url, token):
        self.url = url
        self.headers = {"Authorization": f"user_token {token}"}
    
    def get_ticket(self, id):
        # Faz a chamada real para a API
        resp = requests.get(f"{self.url}/Ticket/{id}", headers=self.headers)
        if resp.status_code == 200:
            return resp.json() # Retorna dados do ticket
        return None

# Uso:
client = MiniGlpi("http://glpi.exemplo.com/apirest.php", "meu_token")
ticket = client.get_ticket(12345)
print(ticket['name'])
```

### Exemplo 2: O Classificador (Mini Agent)
```python
# Lista simples de palavras-chave (em vez de IA complexa)
categorias = {
    "IMPRESSORA": ["papel", "toner", "impressão", "atolamento"],
    "REDE": ["wifi", "internet", "cabo", "navegar"],
    "EMAIL": ["outlook", "senha", "spam", "anexo"]
}

def classificar_texto(texto):
    texto = texto.lower()
    for cat, palavras in categorias.items():
        for p in palavras:
            if p in texto:
                return cat # Encontrou!
    return "OUTROS"

# Uso:
desc = "Minha impressora está sem toner preto"
categoria = classificar_texto(desc)
print(f"O ticket '{desc}' é da categoria: {categoria}")
```

---

## 4. Ideias de Evolução (Conceitual)

Com base na análise da arquitetura atual, aqui estão caminhos para evolução futura:

1.  **Configuração Centralizada:** Mover todas as variáveis de ambiente e constantes (URLs, Tokens, Thresholds de confiança) para um único arquivo `.env` ou `config.yaml`, facilitando a troca entre TESTE e DTIC.
2.  **Log de Decisão Detalhado:** Fazer o agente salvar não apenas "Classificou X", mas "Classificou X porque encontrou o termo Y e a similaridade foi 0.95". Isso ajuda muito na auditoria.
3.  **Modo "Dry-Run" (Simulação):** Criar uma flag oficial no agente que, quando ativa, *nunca* escreve no GLPI, apenas gera um relatório do que *faria*. Isso dá segurança para testar novas regras em DTICução sem risco.
4.  **Fallback Híbrido:** Se a IA (embeddings) não tiver certeza (confiança < 70%), tentar usar regras de palavras-chave exatas (como no Exemplo 2 acima) para "desempatar" categorias óbvias.

---

## 5. Referências de Estudo

Para aprofundar seu conhecimento técnico nestas áreas:

*   **API REST e Requests:** Pesquise sobre "Python Requests tutorial" e "REST API concepts". Entender verbos HTTP (GET, POST, PUT) é essencial para o GLPI.
*   **NLP Básico:** Pesquise sobre "Bag of Words vs Embeddings". Vai ajudar a entender a diferença entre buscar palavras-chave e buscar "sentido".
*   **Estrutura de Projetos Python:** Pesquise sobre "Python Project Layout" ou "Clean Architecture basics".
