import json
from typing import List, Dict, Optional
from glpi_agent.glpi_client import GlpiClient


def ensure_categories(prod: GlpiClient, test: GlpiClient) -> Dict[str, int]:
    prod_map = prod.categories_map()
    test_map = test.categories_map()
    for name in prod_map.keys():
        if name not in test_map:
            cid = test.create_category(name)
            if cid is not None:
                test_map[name] = cid
    return test_map


def clone_tickets_selective(ticket_ids: Optional[List[int]] = None, limit: int = 100) -> Dict[str, int]:
    prod = GlpiClient(environment="prod")
    test = GlpiClient(environment="test")
    prod.init_session()
    test.init_session()
    if not prod.session_token or not test.session_token:
        return {"requested": len(ticket_ids or []), "cloned": 0, "error": 1}
    test_cat_map = ensure_categories(prod, test)
    cloned = 0
    fetched = 0
    start = 0
    page_size = 500
    while fetched < limit:
        end = start + page_size - 1
        batch = prod.list_items_range("Ticket", start, end)
        if not batch:
            break
        for it in batch:
            if fetched >= limit:
                break
            tid = int(it.get("id"))
            if ticket_ids and tid not in ticket_ids:
                continue
            name = str(it.get("name", ""))
            content = str(it.get("content", ""))
            cat_id = it.get("itilcategories_id")
            cat_name = prod.get_category_name(cat_id)
            target_cat_id = test_cat_map.get(cat_name)
            if target_cat_id is None and cat_name:
                target_cat_id = test.create_category(cat_name)
                if target_cat_id:
                    test_cat_map[cat_name] = target_cat_id
            new_id = test.create_ticket(name=f"[CLONE {tid}] {name}", content=content, category_id=target_cat_id)
            if new_id:
                test.add_followup(new_id, f"Clonado de produção ticket_id={tid}")
                cloned += 1
            fetched += 1
        start += page_size
    return {"requested": min(limit, fetched), "cloned": cloned}

