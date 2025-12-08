
# Prompts Library for Data Curation

class CuratorPrompts:
    
    # 1. Binary Judge (Fast Check)
    # Checks if the current category makes sense for the ticket
    BINARY_JUDGE_SYSTEM = """
Você é um auditor de qualidade para um sistema de tickets de TI.
Sua função é verificar se a categorização atual de um ticket está correta.
Responda APENAS em JSON.
"""

    BINARY_JUDGE_USER_TEMPLATE = """
Analise este ticket:

TITULO: {title}
DESCRICAO: {description}

CATEGORIA ATUAL: {current_category}

A categoria atual descreve corretamente o problema relatado?
Se for vagamente relacionada mas existir uma melhor, marque como "suspect".
Se estiver errada, marque como "incorrect".
Se estiver correta, marque como "correct".

Responda no formato JSON:
{{
    "status": "correct" | "incorrect" | "suspect",
    "reason": "breve justificativa em pt-br"
}}
"""

    # 2. Recategorizer (Deep Fix)
    # Suggests the best category from the official list
    RECATEGORIZER_SYSTEM = """
Você é um especialista em triagem de tickets de TI (Helpdesk).
Sua tarefa é classificar tickets na categoria mais adequada dentro da taxonomia oficial.
Seja preciso e objetivo.
"""

    RECATEGORIZER_USER_TEMPLATE = """
Classifique o seguinte ticket na melhor categoria disponível.

TITULO: {title}
DESCRICAO: {description}

LISTA DE CATEGORIAS OFICIAIS (ID - NOME):
{category_list_text}

Instruções:
1. Ignore a categoria antiga se estiver errada.
2. Escolha o ID que melhor se adequa tecnicamente ao problema.
3. Se nenhuma categoria for adequada, use null.

Responda ESTRITAMENTE em JSON:
{{
    "suggested_category_id": <int> ou null,
    "confidence": <float entre 0.0 e 1.0>,
    "reasoning": "breve analise do porquê desta escolha"
}}
"""
