"""
Validate SIS Data - Quick Check
Purpose: Verify data was synced correctly to sis schema
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import Database
from src.modules.dtic.metadata import Entity, Group, ITILCategory, Location

def validate_sis_data():
    """Quick validation of SIS synced data."""
    
    print("=" * 70)
    print("SIS DATA VALIDATION")
    print("=" * 70)
    print(f"\n[INFO] Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        session = Database.get_session(context="sis")
        
        # Count records in each table
        entity_count = session.query(Entity).count()
        location_count = session.query(Location).count()
        group_count = session.query(Group).count()
        category_count = session.query(ITILCategory).count()
        
        print("[1/2] Contagem de Registros:")
        print(f"  - Entidades: {entity_count}")
        print(f"  - Localizações: {location_count}")
        print(f"  - Grupos: {group_count}")
        print(f"  - Categorias: {category_count}")
        
        # Sample data
        print("\n[2/2] Exemplos de Dados:")
        
        if entity_count > 0:
            entity = session.query(Entity).first()
            print(f"\n  Entidade #1:")
            print(f"    ID: {entity.id}")
            print(f"    Nome: {entity.name}")
            print(f"    Nome Completo: {entity.completename}")
        
        if category_count > 0:
            category = session.query(ITILCategory).first()
            print(f"\n  Categoria #1:")
            print(f"    ID: {category.id}")
            print(f"    Nome: {category.name}")
            print(f"    Nome Completo: {category.completename}")
        
        session.close()
        
        # Summary
        total = entity_count + location_count + group_count + category_count
        print("\n" + "=" * 70)
        print(f"[OK] VALIDAÇÃO CONCLUÍDA")
        print(f"  ✓ Total de registros no schema SIS: {total}")
        print("=" * 70)
        
        return total > 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_sis_data()
    exit(0 if success else 1)
