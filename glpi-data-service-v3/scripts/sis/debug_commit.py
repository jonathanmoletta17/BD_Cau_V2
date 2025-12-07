"""
Debug de Commit - Verifica se dados estão sendo salvos
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import Database, config
from src.core.glpi_client import GLPIClient
from src.modules.dtic.metadata import Entity
from sqlalchemy import text

print("=" * 80)
print("DEBUG: TESTE DE COMMIT NO SCHEMA SIS")
print("=" * 80)

# Test 1: Insert manual com commit explícito
print("\n[1/3] Teste de INSERT manual...")
session = Database.get_session(context="sis")

# Verificar schema atual
result = session.execute(text("SELECT current_schema()"))
current = result.scalar()
print(f"  Schema atual: {current}")

# Tentar inserir uma entidade de teste
print("\n  Inserindo entidade de teste...")
test_entity = Entity(
    id=99999,
    name="TESTE - Validação",
    completename="TESTE - Validação",
    level=1,
    entities_id=None
)
session.add(test_entity)
session.commit()
print("  ✓ Commit executado")

# Verificar se foi salvo
session_check = Database.get_session(context="sis")
count = session_check.execute(text("SELECT COUNT(*) FROM glpi_entities WHERE id = 99999")).scalar()
print(f"  Registros com id=99999: {count}")

if count > 0:
    print("  ✓ SUCESSO: Dados foram salvos!")
    # Limpar teste
    session_check.execute(text("DELETE FROM glpi_entities WHERE id = 99999"))
    session_check.commit()
    print("  ✓ Registro de teste removido")
else:
    print("  ✗ FALHA: Dados NÃO foram salvos!")

session.close()
session_check.close()

# Test 2: Verificar se sync_metadata está commitando
print("\n[2/3] Re-executando sync de metadados com debug...")

session = Database.get_session(context="sis")

try:
    with GLPIClient(
        config.GLPI_SIS_URL,
        config.GLPI_SIS_APP_TOKEN,
        config.GLPI_SIS_USER_TOKEN
    ) as client:
        
        # Buscar apenas 5 entidades
        entities = client.make_request('Entity', {'range': '0-4'})
        print(f"  API retornou {len(entities)} entidades")
        
        for ent in entities:
            entity = Entity(
                id=ent['id'],
                name=ent.get('name'),
                completename=ent.get('completename'),
                level=ent.get('level'),
                entities_id=ent.get('entities_id') if ent.get('entities_id') != 0 else None
            )
            session.merge(entity)
        
        print(f"  Executando commit...")
        session.commit()
        print(f"  ✓ Commit executado")
        
        # Verificar imediatamente
        count = session.execute(text("SELECT COUNT(*) FROM glpi_entities")).scalar()
        print(f"  Contagem após commit: {count}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    session.rollback()

session.close()

# Test 3: Verificar contagem final
print("\n[3/3] Verificação final...")
session_final = Database.get_session(context="sis")
count = session_final.execute(text("SELECT COUNT(*) FROM glpi_entities")).scalar()
print(f"  Total de entidades no banco: {count}")
session_final.close()

print("\n" + "=" * 80)
