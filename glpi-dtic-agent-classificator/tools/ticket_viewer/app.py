#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
import json
import os

# Resolve project root and import GLPI client from project root
CV_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
if CV_ROOT not in sys.path:
    sys.path.append(CV_ROOT)
try:
    from glpi_agent.glpi_client import GlpiClient
except ModuleNotFoundError:
    import importlib.util as iu
    _mod_path = os.path.join(CV_ROOT, 'glpi_agent', 'glpi_client.py')
    spec = iu.spec_from_file_location('glpi_client', _mod_path)
    glpi_client = iu.module_from_spec(spec)
    spec.loader.exec_module(glpi_client)
    GlpiClient = glpi_client.GlpiClient

app = Flask(__name__, static_folder='static', template_folder='templates')

_categories_cache = {}

STATUS_NAMES = {1: "Novo", 2: "Em Progresso", 3: "Pendente", 4: "Solucionado", 5: "Fechado", 6: "Cancelado"}

ADMIN_DELETE_TOKEN = os.environ.get('ADMIN_DELETE_TOKEN', '').strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tickets')
def get_tickets():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'date_mod')
    sort_dir = request.args.get('sort_dir', 'desc')

    tickets = load_tickets()

    key_map = {
        'id': lambda t: int(t.get('id', 0)),
        'name': lambda t: (t.get('name') or '').lower(),
        'category_name': lambda t: (t.get('category_name') or '').lower(),
        'status_name': lambda t: (t.get('status_name') or '').lower(),
        'date_creation': lambda t: t.get('date_creation') or t.get('date') or '',
        'date_mod': lambda t: t.get('date_mod') or ''
    }
    key_fn = key_map.get(sort_by, key_map['date_mod'])
    reverse = (sort_dir.lower() == 'desc')
    tickets.sort(key=key_fn, reverse=reverse)

    filtered = tickets
    if category:
        filtered = [t for t in filtered if str(t.get('itilcategories_id')) == category]
    if status:
        filtered = [t for t in filtered if str(t.get('status')) == status]
    if search:
        filtered = [t for t in filtered if search in str(t.get('id')) or search in t.get('name', '').lower()]

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    return jsonify({'tickets': paginated, 'total': total, 'page': page, 'per_page': per_page, 'total_pages': (total + per_page - 1) // per_page if total > 0 else 1})

@app.route('/api/categories')
def get_categories():
    categories = load_categories()
    seen = set()
    cat_list = []
    for cat_id, name in categories.items():
        if name in seen:
            continue
        seen.add(name)
        cat_list.append({'id': cat_id, 'name': name})
    return jsonify(sorted(cat_list, key=lambda x: x['name']))

@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id: int):
    hdr_token = request.headers.get('X-Admin-Token', '')
    if not ADMIN_DELETE_TOKEN or hdr_token != ADMIN_DELETE_TOKEN:
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
    try:
        client = GlpiClient('test')
        client.init_session()
        success = client.delete_item('Ticket', int(ticket_id))
        if success:
            return jsonify({'ok': True, 'id': ticket_id})
        return jsonify({'ok': False, 'error': 'Falha ao excluir no GLPI'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Exception: {str(e)}'}), 500

@app.route('/api/stats')
def get_stats():
    tickets = load_tickets()
    cat_counts = {}
    status_counts = {}
    for ticket in tickets:
        cat_name = ticket.get('category_name', 'Sem categoria')
        status = ticket.get('status_name', 'Desconhecido')
        cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
    return jsonify({'total': len(tickets), 'by_category': cat_counts, 'by_status': status_counts})

def load_tickets():
    tickets = fetch_from_api()
    categories = load_categories()
    for ticket in tickets:
        cat_id = ticket.get('itilcategories_id', 0)
        cat_name = 'Sem categoria'
        if cat_id and cat_id != 0:
            cat_name = categories.get(str(cat_id), categories.get(cat_id, 'Sem categoria'))
        ticket['category_name'] = cat_name
        ticket['status_name'] = STATUS_NAMES.get(ticket.get('status', 1), 'Desconhecido')
    return tickets

def fetch_from_api():
    try:
        client = GlpiClient('test')
        client.init_session()
        tickets = client.search_items('Ticket', {'range': '0-11999'})
        return tickets or []
    except Exception:
        return []

def load_categories():
    global _categories_cache
    if not _categories_cache:
        _categories_cache = {'0': 'Sem categoria'}
        # Optional: load id_mappings.json if present under context-validation/data/
        try:
            mapping_file = os.path.join(CV_ROOT, 'data', 'id_mappings.json')
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    prod_cats = data.get('categories', {})
                    for prod_id, info in prod_cats.items():
                        name = info.get('completename') or info.get('name')
                        if name:
                            _categories_cache[str(prod_id)] = name
        except Exception:
            pass
        # Load test categories from API
        try:
            client = GlpiClient('test')
            client.init_session()
            categories = client.search_items('ITILCategory', {'range': '0-999'})
            for cat in categories or []:
                cat_id = str(cat.get('id'))
                if cat_id not in _categories_cache:
                    name = cat.get('completename') or cat.get('name', 'Sem nome')
                    _categories_cache[cat_id] = name
        except Exception:
            pass
    return _categories_cache

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
