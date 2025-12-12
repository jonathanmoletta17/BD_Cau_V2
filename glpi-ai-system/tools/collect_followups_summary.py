import sys
import re
import json
from collections import Counter, defaultdict
from pathlib import Path

# Ensure imports work (project root)
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "glpi-data-service"))
sys.path.insert(0, str(project_root / "glpi-data-service" / "src"))

from src.core.config import config
from src.core.glpi_client import GLPIClient


def normalize_text(t: str) -> str:
    t = t or ""
    t = t.lower()
    t = re.sub(r"[\r\n]+", " ", t)
    return t


def main():
    url = config.get_glpi_url("dtic")
    app_token = config.get_glpi_app_token("dtic")
    user_token = config.get_glpi_user_token("dtic")

    if not url or not app_token or not user_token:
        print(json.dumps({"error": "Missing GLPI config env vars"}, ensure_ascii=False))
        return

    client = GLPIClient(url, app_token, user_token)
    try:
        client.init_session()
    except Exception as e:
        print(json.dumps({"error": f"Session error: {e}"}, ensure_ascii=False))
        return

    try:
        tickets = client.make_request("Ticket", params={"range": "0-99", "sort": "id", "order": "DESC"})
    except Exception as e:
        print(json.dumps({"error": f"List error: {e}"}, ensure_ascii=False))
        client.close_session()
        return

    questions = []
    keywords_counter = Counter()
    question_counter = Counter()
    examples_good = []
    examples_sensitive = []
    by_category = defaultdict(lambda: {"count": 0, "questions": Counter(), "keywords": Counter()})

    keyword_list = [
        "local","entidade","sala","patrimônio","equipamento","print","erro","mensagem","horário","vpn","rede",
        "internet","e-mail","acesso","perfil","grupo","categoria","prioridade","fila","impressora","carregador",
        "sis","dtic","patrimonio","senha","token","cpf","telefone","anexo","anexar","reiniciar","teste","reproduzir","passos"
    ]

    for t in tickets or []:
        tid = t.get("id")
        cat_id = t.get("itilcategories_id")

        try:
            followups = client.make_request(f"Ticket/{tid}/ITILFollowup")
        except Exception:
            followups = []

        for f in followups or []:
            content = f.get("content") or ""
            c_norm = normalize_text(content)

            # Extract questions
            for q in re.split(r"[.!?]", content):
                q2 = q.strip()
                if ("?" in q) or re.search(r"^(pode|poderia|favor|por favor|informe|envie|anexe|confirme)\b", q2.lower()):
                    if len(q2) >= 8:
                        questions.append(q2)
                        question_counter[q2.lower()] += 1
                        by_category[str(cat_id)]["questions"][q2.lower()] += 1

            # Keyword counts
            for kw in keyword_list:
                if kw in c_norm:
                    keywords_counter[kw] += 1
                    by_category[str(cat_id)]["keywords"][kw] += 1
            by_category[str(cat_id)]["count"] += 1

            # Examples
            if any(s in c_norm for s in ["senha", "token", "cpf"]):
                examples_sensitive.append(content.strip())
            elif any(s in c_norm for s in ["favor", "pode", "poderia", "anexe", "informe", "confirme"]):
                examples_good.append(content.strip())

    client.close_session()

    top_questions = [q for q, _ in question_counter.most_common(15)]
    top_keywords = [k for k, _ in keywords_counter.most_common(15)]

    def top_by_cat(cdict, n=5):
        out = {}
        for cat, data in cdict.items():
            if data["count"] == 0:
                continue
            out[cat] = {
                "count": data["count"],
                "questions": [q for q, _ in data["questions"].most_common(n)],
                "keywords": [k for k, _ in data["keywords"].most_common(n)]
            }
        return out

    summary = {
        "sample_size_followups": sum(v["count"] for v in by_category.values()),
        "top_questions": top_questions,
        "top_keywords": top_keywords,
        "by_category": top_by_cat(by_category, 5),
        "examples_good": examples_good[:8],
        "examples_sensitive": examples_sensitive[:8]
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
