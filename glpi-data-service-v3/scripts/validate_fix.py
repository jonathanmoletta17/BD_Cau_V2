"""
Script de Validação de Qualidade de Dados
==========================================
Verifica se os dados no banco estão limpos e normalizados.
"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core import Database

def validate():
    print("=" * 60)
    print("VALIDAÇÃO DE QUALIDADE DE DADOS")
    print("=" * 60)
    
    session = Database.get_session(context="dtic")
    
    try:
        # Contagem total
        total = session.execute(text(
            "SELECT COUNT(*) FROM dtic.ticket_changes"
        )).scalar()
        print(f"Total de Registros: {total:,}")
        print("-" * 40)
        
        # 1. Verificar EMPTY
        empty_count = session.execute(text("""
            SELECT COUNT(*) FROM dtic.ticket_changes 
            WHERE valor_antigo = 'EMPTY' OR valor_novo = 'EMPTY'
        """)).scalar()
        print(f"1. Literais 'EMPTY':      {empty_count:,} " + 
              ("✅" if empty_count == 0 else "❌"))
        
        # 2. Verificar Nomes Invertidos
        inverted = session.execute(text("""
            SELECT COUNT(*) FROM dtic.ticket_changes 
            WHERE usuario_nome ~ '\\(\\d+\\)$'
        """)).scalar()
        print(f"2. Nomes incorretos:      {inverted:,} " + 
              ("✅" if inverted == 0 else "❌"))
        
        # 3. Verificar campos mapeados
        unknown = session.execute(text("""
            SELECT COUNT(*) FROM dtic.ticket_changes 
            WHERE campo = 'UNKNOWN'
        """)).scalar()
        sistema = session.execute(text("""
            SELECT COUNT(*) FROM dtic.ticket_changes 
            WHERE campo = 'Alteração de Sistema'
        """)).scalar()
        print(f"3. Campo 'UNKNOWN':       {unknown:,} " + 
              ("✅" if unknown == 0 else "⚠️"))
        print(f"   Campo 'Alt. Sistema':  {sistema:,}")
        
        # 4. Verificar IDs recuperados
        null_ids = session.execute(text(
            "SELECT COUNT(*) FROM dtic.ticket_changes WHERE usuario_id IS NULL"
        )).scalar()
        with_ids = total - null_ids
        pct = (with_ids / total * 100) if total > 0 else 0
        print(f"4. IDs preenchidos:       {with_ids:,} ({pct:.1f}%)")
        
        print("-" * 40)
        
        # Resumo
        if empty_count == 0 and inverted == 0 and unknown == 0:
            print("\n✅ SUCESSO: Dados 100% limpos!")
        elif empty_count == 0 and inverted == 0:
            print("\n✅ SUCESSO: Dados limpos (campos legado OK)!")
        else:
            print("\n⚠️ AVISO: Existem dados a corrigir.")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    validate()
