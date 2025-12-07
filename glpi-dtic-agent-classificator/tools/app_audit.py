import streamlit as st
import json
import os
import re

# Configuration
st.set_page_config(page_title="Data Audit System", layout="wide")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_PATH = os.path.join(PROJECT_ROOT, "data", "audit_queue.json")
DECISIONS_PATH = os.path.join(PROJECT_ROOT, "data", "audit_decisions.json")
CONTEXTS_PATH = os.path.join(PROJECT_ROOT, "agent", "manual_contexts.json")

# --- Helper Functions ---
def clean_html(raw_html):
    """Remove HTML tags and entities."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = cleantext.replace('&nbsp;', ' ').replace('&#60;', '<').replace('&#62;', '>')
    return cleantext.strip()

def load_categories():
    """Load valid categories from manual_contexts.json"""
    if not os.path.exists(CONTEXTS_PATH):
        return []
    with open(CONTEXTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return sorted(list(data.keys()))

def load_data():
    if not os.path.exists(QUEUE_PATH):
        st.error(f"Queue file not found: {QUEUE_PATH}")
        return []
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_decisions():
    if not os.path.exists(DECISIONS_PATH):
        return []
    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_decision(item, decision_type, final_category):
    decisions = load_decisions()
    
    # Check if ID already exists (update if so)
    processed_ids = [d["id"] for d in decisions]
    if item["id"] in processed_ids:
        # Remove old entry to replace it
        decisions = [d for d in decisions if d["id"] != item["id"]]

    # Create decision record
    record = {
        "id": item["id"],
        "text": item["text"],
        "original_human_label": item["human_label"],
        "original_ai_label": item["ai_label"],
        "decision": decision_type, # 'human', 'ai', 'custom'
        "final_category": final_category
    }
    
    decisions.append(record)
    
    with open(DECISIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)

# --- Main App ---
def main():
    st.title("⚖️ Tribunal da IA: Auditoria de Dataset")
    
    # Load Data
    queue = load_data()
    decisions = load_decisions()
    all_categories = load_categories()
    
    # Filter processed items
    processed_ids = {d["id"] for d in decisions}
    pending_queue = [item for item in queue if item["id"] not in processed_ids]
    
    # Progress Bar
    total = len(queue)
    completed = len(decisions)
    progress = completed / total if total > 0 else 0
    st.progress(progress)
    st.caption(f"Progresso: {completed}/{total} tickets auditados")

    if not pending_queue:
        st.success("🎉 Auditoria Completa! Todos os conflitos foram resolvidos.")
        st.balloons()
        return

    # Pick current item
    item = pending_queue[0]
    
    # --- Layout ---
    st.divider()
    st.subheader(f"Ticket #{item['id']}")
    
    # Ticket Content Box (Cleaned)
    with st.container(border=True):
        cleaned_text = clean_html(item["text"])
        st.markdown(f"**Descrição:** {cleaned_text}")
        # Show raw text in expander if needed
        with st.expander("Ver texto original (Raw)"):
            st.code(item["text"], language="html")

    st.divider()

    col1, col2 = st.columns(2)

    # --- LEFT CORNER: HUMAN ---
    with col1:
        st.info("👤 **Humano (Original)**")
        st.metric(label="Categoria Histórica", value=item["human_label"])
        
        if st.button("✅ Manter Decisão Humana", use_container_width=True, type="secondary"):
            save_decision(item, "human", item["human_label"])
            st.rerun()

    # --- RIGHT CORNER: AI ---
    with col2:
        st.success(f"🤖 **Inteligência Artificial ({item['ai_confidence']*100:.1f}%)**")
        st.metric(label="Categoria Sugerida", value=item["ai_label"])
        
        with st.expander("🧠 Por que a IA escolheu isso?", expanded=False):
            st.write(item["ai_reasoning"])
            
        if st.button("✨ Aceitar Sugestão da IA", use_container_width=True, type="primary"):
            save_decision(item, "ai", item["ai_label"])
            st.rerun()

    # --- CUSTOM OPTION ---
    st.divider()
    st.warning("✏️ **Correção Manual** (Use se ambas estiverem erradas)")
    
    # Intelligent default index
    try:
        default_idx = all_categories.index(item["ai_label"])
    except ValueError:
        default_idx = 0
        
    selected_category = st.selectbox(
        "Selecione a categoria correta:", 
        options=all_categories,
        index=default_idx
    )
    
    if st.button("💾 Salvar Correção Manual", type="primary"):
        save_decision(item, "custom", selected_category)
        st.rerun()

if __name__ == "__main__":
    main()

