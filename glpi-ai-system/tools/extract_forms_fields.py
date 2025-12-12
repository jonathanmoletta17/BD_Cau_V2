import sys
import json
import re
from pathlib import Path
from collections import defaultdict
from sqlalchemy import text

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "glpi-data-service"))
sys.path.insert(0, str(project_root / "glpi-data-service" / "src"))

from src.core import Database


def derive_form_name(title: str, fields: dict) -> str:
    t = (title or "").lower()
    tipo = None
    for k, v in fields.items():
        if k.lower().strip() in ["tipo", "tipo de serviço"]:
            tipo = v.strip()
            break
    if tipo:
        base = tipo
        if "office" in t:
            return f"Office 365 - {base}"
        if "outlook" in t or "caixa" in t:
            return f"Outlook - {base}"
        return base
    if "office 365" in t:
        return "Office 365"
    if "outlook" in t or ("caixa" in t and "compart" in t):
        return "Outlook - Caixa Compartilhada"
    if "acesso a sistemas rede piratini" in t:
        return "Acesso a Sistemas - Rede Piratini"
    if "usuário de rede" in t or ("novo usuário" in t):
        return "Criação de Usuário de Rede"
    return "Formulário Genérico"


def parse_fields_from_text(desc: str) -> dict:
    fields = {}
    if not desc:
        return fields
    text_norm = desc.replace("\r", "")
    text_norm = re.sub(r"(?i)dados do formulário.*?(?=\d+\))", "", text_norm, flags=re.S)
    pattern = re.compile(r"\s*\d+\)\s*([^:]+?)\s*:\s*:?\s*(.*?)(?=\s*\d+\)\s|$)", re.S)
    for match in pattern.finditer(text_norm):
        label = match.group(1).strip()
        value = match.group(2).strip()
        if label:
            fields[label] = value
    if not fields:
        lines = text_norm.split("\n")
        rx_plain = re.compile(r"^\s*([A-Za-zÁ-Úá-ú0-9_/ .()-]+?)\s*:\s*(.*)$")
        for ln in lines:
            m2 = rx_plain.match(ln)
            if m2:
                label = m2.group(1).strip()
                value = m2.group(2).strip()
                if label and label.lower() not in ["dados do formulário", "dados gerais", "detalhamento"]:
                    fields[label] = value
    return fields


def main():
    session = Database.get_session(context="dtic")
    try:
        rows = session.execute(text("""
            SELECT glpi_id, titulo, descricao
            FROM dtic.tickets
            WHERE descricao ILIKE '%Dados do formulário%'
              AND is_deleted = FALSE
            ORDER BY atualizado_em DESC
            LIMIT 500;
        """)).fetchall()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        session.close()
        return

    forms = defaultdict(lambda: {"count": 0, "fields": set(), "examples": []})

    for gid, titulo, descricao in rows:
        fields = parse_fields_from_text(descricao or "")
        form_name = derive_form_name(titulo or "", fields)
        forms[form_name]["count"] += 1
        for k in fields.keys():
            forms[form_name]["fields"].add(k)
        if len(forms[form_name]["examples"]) < 5:
            sample = {k: fields.get(k, "") for k in list(fields.keys())[:10]}
            forms[form_name]["examples"].append({"id": gid, "titulo": titulo, "sample_fields": sample})

    summary = []
    for name, data in forms.items():
        summary.append({
            "form": name,
            "count": data["count"],
            "fields": sorted(list(data["fields"])),
            "examples": data["examples"]
        })

    session.close()
    print(json.dumps({"forms": summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
