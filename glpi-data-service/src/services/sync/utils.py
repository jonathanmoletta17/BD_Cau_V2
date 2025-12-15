
import hashlib
import html
import re
from datetime import datetime
# --- Clean Utilities ---
import re
from typing import Optional, Dict
from sqlalchemy import text

# Mapeamento completo de campos GLPI (id_search_option -> nome)
FIELD_MAPPING = {
    0: "Alteração de Sistema",
    1: "Título", 2: "ID", 3: "Prioridade", 4: "Requerente", 5: "Técnico",
    6: "Atribuído a um fornecedor", 7: "Categoria", 8: "Grupo técnico",
    9: "Origem da requisição", 10: "Urgência", 11: "Impacto", 12: "Status",
    13: "Elementos associados", 14: "Tipo", 15: "Data de abertura",
    16: "Data de fechamento", 17: "Data da solução", 18: "Tempo para solução",
    19: "Última atualização", 20: "Categoria da tarefa", 21: "Descrição",
    22: "Autor", 23: "Tipo de solução", 24: "Solução", 25: "Descrição do acompanhamento",
    26: "Descrição da tarefa", 27: "Número de acompanhamentos", 28: "Número de tarefas",
    29: "Origem da requisição (acompanhamento)", 30: "SLAs Tempo para solução",
    31: "Tipo de satisfação", 32: "SLAs Nível de escalação", 33: "Status da tarefa",
    34: "E-mail para o acompanhamento", 35: "Acompanhamento por e-mail",
    36: "Data do acompanhamento", 37: "SLAs Tempo para atendimento",
    38: "Qualquer status da solução", 39: "Último status da solução",
    40: "Todos chamados relacionados", 41: "Número de todos chamados relacionados",
    42: "Custo de tempo", 43: "Custo fixo", 44: "Custo de material",
    45: "Duração total", 46: "Número de chamados duplicados",
    47: "Chamados duplicados", 48: "Custo total", 49: "Custo - Duração",
    50: "Chamados pai", 51: "Um mínimo de validação é necessária",
    52: "Aprovação", 53: "Comentários da requisição", 54: "Comentários da validação",
    55: "Status de aprovação", 56: "Data da requisição", 57: "Data da validação",
    58: "Requerente (validação)", 59: "Aprovador", 60: "Data de criação (satisfação)",
    61: "Data de resposta (satisfação)", 62: "Satisfação", 63: "Comentários (satisfação)",
    64: "Última edição por", 65: "Grupo observador", 66: "Observador",
    67: "Chamados filhos", 68: "Número de chamados filho", 69: "Número de chamados pai",
    70: "Ticket Relacionado", 71: "Grupo requerente",
    79: "Localização (alternativo)", 80: "Entidade", 82: "Tempo para resolver excedido",
    83: "Localização", 84: "Número do prédio", 85: "Número da sala",
    86: "Comentários da localização", 87: "Nome do requisitante",
    88: "Telefone do requisitante", 91: "Acompanhamento privado",
    92: "Chamado privado", 93: "Autor (acompanhamento)", 94: "Autor (tarefa)",
    95: "Técnico encarregado", 96: "Duração (tarefa)", 97: "Data (tarefa)",
    99: "Campo personalizado", 100: "Campo adicional",
    101: "Endereço", 102: "Código postal", 103: "Cidade", 104: "Estado",
    105: "País", 107: "Descrição alternativa", 109: "Template de acompanhamento",
    110: "Tipo de acompanhamento", 111: "Origem do acompanhamento",
    112: "Grupo encarregado", 115: "Campo interno", 118: "Campo técnico",
    119: "Número de documentos", 120: "Versão ITIL", 129: "Item de configuração",
    131: "Tipos de itens associados", 142: "Documentos", 150: "Leve em conta o tempo",
    151: "Tempo para solução + Progresso", 152: "Hora de fechamento",
    153: "Tempo de espera", 154: "Tempo de solução", 155: "Tempo para atendimento",
    158: "Tempo para atendimento + Progresso", 159: "Tempo para adquirir excedido",
    173: "Data inicial (tarefa)", 174: "Data final (tarefa)", 175: "Modelo de tarefa",
    180: "Tempo interno para solução", 181: "Tempo interno para solução + Progresso",
    182: "Tempo interno para resolver excedido", 185: "Tempo interno para atendimento",
    186: "Tempo interno para atendimento + Progresso", 187: "Tempo interno para possuir excedido",
    188: "Próximo nível de escalonamento", 190: "OLA Tempo interno para atendimento",
    191: "OLA Tempo interno para solução", 192: "OLA Nível de escalação",
    193: "Contract", 194: "Tipo de contrato", 200: "Número de problemas",
    201: "Problema", 202: "Status (problema)", 203: "Data da solução (problema)",
    204: "Data de abertura (problema)", 400: "Motivo de pendência",
    998: "Latitude", 999: "Longitude"
}

def clean_usuario_nome(nome: str) -> Optional[str]:
    if not nome or not isinstance(nome, str):
        return None
    nome_sem_id = re.sub(r'\s*\(\d+\)\s*$', '', nome).strip()
    if nome_sem_id.startswith("- "):
        resto = nome_sem_id[2:].strip()
        tokens = resto.split()
        if len(tokens) > 1:
            primeiro_nome = tokens[-1]
            sobrenomes = tokens[:-1]
            return f"{primeiro_nome} {' '.join(sobrenomes)}"
        return resto
    return nome_sem_id if nome_sem_id else None

def get_campo_name(campo_id) -> str:
    if campo_id is None:
        return "Alteração de Sistema"
    try:
        cid = int(campo_id)
        return FIELD_MAPPING.get(cid, f"Campo {cid}")
    except (ValueError, TypeError):
        return "Alteração de Sistema"

def treat_empty(val) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, str):
        val_stripped = val.strip()
        if val_stripped in ("", "EMPTY", "NULL", "None"):
            return None
        return val_stripped
    return str(val)

def load_user_map(session) -> Dict[str, int]:
    try:
        users = session.execute(text(
            "SELECT id, name, firstname, realname FROM dtic.glpi_users"
        )).fetchall()
        mapping = {}
        for u in users:
            parts = []
            if u.firstname: parts.append(u.firstname)
            if u.realname: parts.append(u.realname)
            full_name = " ".join(parts).strip()
            if full_name: mapping[full_name] = u.id
            if u.name: mapping[u.name] = u.id
        return mapping
    except Exception:
        return {}

def clean_str(val):
    if isinstance(val, str) and not val.strip():
        return None
    return val

def get_int(val):
    if val is None or val is False:
        return None
    if isinstance(val, int):
        return val if val != 0 else None
    if isinstance(val, str):
        if not val.strip():
            return None
        if val.isdigit():
            i = int(val)
            return i if i != 0 else None
    return None

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None

def calc_hash(t):
    hash_str = f"{t.get('name', '')}{t.get('content', '')}{t.get('status', '')}{t.get('priority', '')}"
    return hashlib.md5(hash_str.encode()).hexdigest()

def clean_html(raw_html):
    if not raw_html:
        return None
    decoded = html.unescape(str(raw_html))
    decoded = html.unescape(decoded)
    clean = re.sub(r'<[^>]+>', ' ', decoded)
    text_content = " ".join(clean.split())
    return text_content if text_content else None
