let currentPage = 1;
let filters = { category: '', status: '', search: '' };
let sort = { field: 'date_mod', dir: 'desc' };
let autoRefreshInterval = null;
const AUTO_REFRESH_SECONDS = 30;

window.addEventListener('DOMContentLoaded', function () {
    loadCategories();
    loadStats();
    loadTickets();
    startAutoRefresh();
    updateLastRefreshTime();
});

function startAutoRefresh() {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    autoRefreshInterval = setInterval(() => {
        loadTickets(currentPage);
        loadStats();
        updateLastRefreshTime();
    }, AUTO_REFRESH_SECONDS * 1000);
}

function updateLastRefreshTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('pt-BR');
    let indicator = document.getElementById('lastRefresh');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'lastRefresh';
        indicator.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #238636; color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.3);';
        document.body.appendChild(indicator);
    }
    indicator.innerHTML = `🔄 Última atualização: ${timeStr}`;
}

async function loadTickets(page = 1) {
    currentPage = page;
    const params = new URLSearchParams({
        page: page,
        per_page: 20,
        category: filters.category,
        status: filters.status,
        search: filters.search,
        sort_by: sort.field,
        sort_dir: sort.dir
    });
    try {
        const response = await fetch(`/api/tickets?${params}`);
        const data = await response.json();
        renderTickets(data.tickets);
        renderPagination(data.page, data.total_pages, data.total);
    } catch (error) {
        showError('Erro ao carregar tickets');
    }
}

function renderTickets(tickets) {
    const tbody = document.getElementById('ticketsBody');
    tbody.innerHTML = '';
    if (tickets.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 40px; color: #8b949e;">Nenhum ticket encontrado com os filtros aplicados</td></tr>`;
        return;
    }
    tickets.forEach(ticket => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>#${ticket.id}</td>
            <td>${ticket.name || 'Sem título'}</td>
            <td>${ticket.category_name || 'Sem categoria'}</td>
            <td>${ticket.status_name || 'Desconhecido'}</td>
            <td>${ticket.date_creation || ticket.date || ''}</td>
            <td>${ticket.date_mod || ''}</td>
        `;
        row.onclick = () => showTicketModal(ticket);
        tbody.appendChild(row);
    });
}

function renderPagination(page, totalPages, totalTickets) {
    const container = document.getElementById('pagination');
    container.innerHTML = `
        <button onclick="loadTickets(${page - 1})" ${page === 1 ? 'disabled' : ''}>◀ Anterior</button>
        <span>Página ${page} de ${totalPages} (${totalTickets} tickets)</span>
        <button onclick="loadTickets(${page + 1})" ${page === totalPages ? 'disabled' : ''}>Próximo ▶</button>
    `;
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        const select = document.getElementById('categoryFilter');
        const defaultOption = select.options[0] ? select.options[0].cloneNode(true) : null;
        select.innerHTML = '';
        if (defaultOption) select.appendChild(defaultOption);
        const seenNames = new Set();
        categories.forEach(cat => {
            const name = cat.name || 'Sem nome';
            if (seenNames.has(name)) return;
            seenNames.add(name);
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = name;
            select.appendChild(option);
        });
    } catch (error) {}
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        document.getElementById('totalTickets').textContent = stats.total.toLocaleString('pt-BR');
        const categorized = stats.total - (stats.by_category['Sem categoria'] || 0);
        const uncategorized = stats.by_category['Sem categoria'] || 0;
        document.getElementById('categorizedTickets').textContent = categorized.toLocaleString('pt-BR');
        document.getElementById('uncategorizedTickets').textContent = uncategorized.toLocaleString('pt-BR');
    } catch (error) {}
}

function applyFilters() {
    filters.category = document.getElementById('categoryFilter').value;
    filters.status = document.getElementById('statusFilter').value;
    filters.search = document.getElementById('searchBox').value;
    loadTickets(1);
}

function resetFilters() {
    document.getElementById('categoryFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('searchBox').value = '';
    filters = { category: '', status: '', search: '' };
    loadTickets(1);
}

function showTicketModal(ticket) {
    const modal = document.getElementById('ticketModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    modalTitle.textContent = `Ticket #${ticket.id}`;
    const content = ticket.content || 'Sem descrição';
    const truncatedContent = content.length > 500 ? content.substring(0, 500) + '...' : content;
    modalBody.innerHTML = `
        <p><strong>Título:</strong> ${ticket.name || 'Sem título'}</p>
        <p><strong>Categoria:</strong> ${ticket.category_name || 'Sem categoria'}</p>
        <p><strong>Status:</strong> ${ticket.status_name || 'Desconhecido'}</p>
        <p><strong>ID Categoria:</strong> ${ticket.itilcategories_id || '0'}</p>
        <hr style="border-color: #30363d; margin: 15px 0;">
        <p><strong>Descrição:</strong></p>
        <p style="white-space: pre-wrap; background: #0d1117; padding: 15px; border-radius: 6px; margin-top: 10px;">${truncatedContent}</p>
        <hr style="border-color: #30363d; margin: 15px 0;">
        <div style="display:flex; gap:8px; justify-content:flex-end;">
            <button id="deleteTicketBtn" style="background:#f85149; color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer;">Excluir ticket</button>
            <button onclick="closeModal()" style="background:#30363d; color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer;">Fechar</button>
        </div>
    `;
    modal.style.display = 'block';
    const btn = document.getElementById('deleteTicketBtn');
    if (btn) btn.onclick = () => deleteTicket(ticket.id);
}

function closeModal() { document.getElementById('ticketModal').style.display = 'none'; }

function showError(message) {
    const tbody = document.getElementById('ticketsBody');
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 40px; color: #f85149;">❌ ${message}</td></tr>`;
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('searchBox').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
});

function setSort(field) {
    if (sort.field === field) {
        sort.dir = sort.dir === 'asc' ? 'desc' : 'asc';
    } else {
        sort.field = field;
        sort.dir = field.includes('date') ? 'desc' : 'asc';
    }
    loadTickets(1);
}

function getAdminToken() {
    const key = 'deleteAdminToken';
    let token = localStorage.getItem(key) || '';
    if (!token) {
        token = prompt('Informe o token de deleção (X-Admin-Token):') || '';
        if (token) localStorage.setItem(key, token);
    }
    return token;
}

async function deleteTicket(ticketId) {
    const sure = confirm(`Tem certeza que deseja excluir o ticket #${ticketId}? Esta ação é irreversível.`);
    if (!sure) return;
    const token = getAdminToken();
    if (!token) { alert('Token não informado. Operação cancelada.'); return; }
    try {
        const resp = await fetch(`/api/tickets/${ticketId}`, { method: 'DELETE', headers: { 'X-Admin-Token': token } });
        const data = await resp.json();
        if (resp.ok && data.ok) { alert(`Ticket #${ticketId} excluído com sucesso.`); closeModal(); loadTickets(currentPage); loadStats(); }
        else { alert(`Falha ao excluir: ${data.error || 'Erro desconhecido'}`); }
    } catch (err) { alert(`Erro na requisição: ${err}`); }
}

