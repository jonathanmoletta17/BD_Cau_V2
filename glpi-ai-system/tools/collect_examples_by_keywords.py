import sys
import json
import re
from pathlib import Path
from sqlalchemy import text

# Ensure imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "glpi-data-service"))
sys.path.insert(0, str(project_root / "glpi-data-service" / "src"))

from src.core import Database


def query(session, sql):
    try:
        return session.execute(text(sql)).fetchall()
    except Exception:
        return []


def summarize(rows):
    cpf_re = re.compile(r"\\b\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}\\b")
    email_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")
    phone_re = re.compile(r"\\b\\d{4,5}[- ]?\\d{4}\\b")
    name_hints = ["nome", "servidor", "colaborador", "funcionário", "usuario", "usuário"]
    lotacao_hints = ["lotação", "entidade", "departamento", "setor"]

    examples = []
    stats = {"cpf": 0, "email": 0, "telefone": 0, "nome_mencionado": 0, "lotacao_mencionada": 0, "patrimonio": 0}

    for gid, titulo, desc in rows:
        d = (desc or "")[:600]
        cpfs = cpf_re.findall(d)
        emails = email_re.findall(d)
        phones = phone_re.findall(d)
        nome_flag = any(h in d.lower() for h in name_hints)
        lot_flag = any(h in d.lower() for h in lotacao_hints)
        patr_flag = ("patrim" in d.lower())
        stats["cpf"] += 1 if cpfs else 0
        stats["email"] += 1 if emails else 0
        stats["telefone"] += 1 if phones else 0
        stats["nome_mencionado"] += 1 if nome_flag else 0
        stats["lotacao_mencionada"] += 1 if lot_flag else 0
        stats["patrimonio"] += 1 if patr_flag else 0

        examples.append({
            "id": gid,
            "titulo": titulo,
            "snippet": d,
            "has_cpf": bool(cpfs),
            "has_email": bool(emails),
            "has_telefone": bool(phones),
            "mentions_nome": nome_flag,
            "mentions_lotacao": lot_flag,
            "mentions_patrimonio": patr_flag
        })

    return {"count": len(rows), "examples": examples[:10], "fields_stats": stats}


def main():
    session = Database.get_session(context="dtic")
    try:
        sql_office = """
        SELECT t.glpi_id, t.titulo, t.descricao
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_itilcategories c ON c.id = t.categoria_id
        WHERE (
            c.name ILIKE '%office%' OR c.completename ILIKE '%office%'
            OR t.titulo ILIKE '%office%' OR t.titulo ILIKE '%excel%' OR t.titulo ILIKE '%word%' OR t.titulo ILIKE '%outlook%'
        )
        AND t.is_deleted = FALSE
        ORDER BY t.atualizado_em DESC
        LIMIT 30;
        """

        sql_shared = """
        SELECT t.glpi_id, t.titulo, t.descricao
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_itilcategories c ON c.id = t.categoria_id
        WHERE (
            (t.titulo ILIKE '%caixa%' AND t.titulo ILIKE '%compart%')
            OR (t.descricao ILIKE '%caixa%' AND t.descricao ILIKE '%compart%')
            OR c.name ILIKE '%mailbox%' OR c.completename ILIKE '%mailbox%'
            OR c.name ILIKE '%caixa%' OR c.completename ILIKE '%caixa%'
        )
        AND t.is_deleted = FALSE
        ORDER BY t.atualizado_em DESC
        LIMIT 30;
        """

        sql_user_creation = """
        SELECT t.glpi_id, t.titulo, t.descricao
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_itilcategories c ON c.id = t.categoria_id
        WHERE (
            (t.titulo ILIKE '%cria%' AND t.titulo ILIKE '%usu%')
            OR (t.descricao ILIKE '%cria%' AND t.descricao ILIKE '%usu%')
            OR t.titulo ILIKE '%usuário de rede%' OR t.descricao ILIKE '%usuário de rede%'
            OR (t.titulo ILIKE '%e-mail%' AND t.titulo ILIKE '%cria%')
            OR (t.descricao ILIKE '%e-mail%' AND t.descricao ILIKE '%cria%')
            OR c.name ILIKE '%usuario%' OR c.completename ILIKE '%usuario%'
            OR c.name ILIKE '%user%' OR c.completename ILIKE '%user%'
        )
        AND t.is_deleted = FALSE
        ORDER BY t.atualizado_em DESC
        LIMIT 40;
        """

        rows_office = query(session, sql_office)
        rows_shared = query(session, sql_shared)
        rows_user_creation = query(session, sql_user_creation)

        summary = {
            "office": summarize(rows_office),
            "caixa_compartilhada": summarize(rows_shared),
            "criacao_usuario": summarize(rows_user_creation)
        }
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        session.close()


if __name__ == "__main__":
    main()
