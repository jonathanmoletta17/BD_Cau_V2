"""
Validação de Integridade Referencial - Tabelas Críticas DTIC
=============================================================

Valida consistência e integridade das 7 tabelas principais:
1. glpi_users
2. tickets
3. glpi_profiles
4. glpi_entities
5. glpi_groups
6. glpi_locations
7. glpi_itilcategories
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
from sqlalchemy import text

def check_referential_integrity(session):
    """Verifica integridade referencial entre tabelas"""
    print("\n" + "="*80)
    print("VALIDAÇÃO DE INTEGRIDADE REFERENCIAL - TABELAS CRÍTICAS")
    print("="*80)
    
    issues = []
    warnings = []
    
    # 1. TICKETS → USERS (ultimo_atualizador_id)
    print("\n📊 1. Tickets → Users (ultimo_atualizador_id)")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_users u ON t.ultimo_atualizador_id = u.id
        WHERE t.ultimo_atualizador_id IS NOT NULL AND u.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} tickets com ultimo_atualizador_id inválido")
        print(f"  ❌ {result.orphans} tickets órfãos")
    else:
        print(f"  ✅ OK - Todos os tickets têm usuário válido")
    
    # 2. TICKETS → CATEGORIES
    print("\n📊 2. Tickets → Categories (categoria_id)")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_itilcategories c ON t.categoria_id = c.id
        WHERE t.categoria_id IS NOT NULL AND c.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} tickets com categoria_id inválida")
        print(f"  ❌ {result.orphans} tickets órfãos")
    else:
        print(f"  ✅ OK - Todas as categorias são válidas")
    
    # Estatísticas de categorias
    stats = session.execute(text("""
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(categoria_id) as com_categoria,
            COUNT(*) - COUNT(categoria_id) as sem_categoria
        FROM dtic.tickets
    """)).fetchone()
    
    pct_sem = (stats.sem_categoria / stats.total_tickets * 100) if stats.total_tickets > 0 else 0
    print(f"  📈 {stats.total_tickets:,} tickets total")
    print(f"  📈 {stats.com_categoria:,} com categoria ({100-pct_sem:.1f}%)")
    print(f"  📈 {stats.sem_categoria:,} sem categoria ({pct_sem:.1f}%)")
    
    if pct_sem > 10:
        warnings.append(f"⚠️  {pct_sem:.1f}% dos tickets sem categoria")
    
    # 3. TICKETS_GROUPS → TICKETS
    print("\n📊 3. Tickets_Groups → Tickets")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.tickets_groups tg
        LEFT JOIN dtic.tickets t ON tg.ticket_id = t.id
        WHERE t.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} tickets_groups órfãos")
        print(f"  ❌ {result.orphans} relacionamentos órfãos")
    else:
        print(f"  ✅ OK - Todos os relacionamentos válidos")
    
    # 4. TICKETS_GROUPS → GROUPS
    print("\n📊 4. Tickets_Groups → Groups")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.tickets_groups tg
        LEFT JOIN dtic.glpi_groups g ON tg.group_id = g.id
        WHERE g.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} tickets_groups com group_id inválido")
        print(f"  ❌ {result.orphans} grupos inválidos")
    else:
        print(f"  ✅ OK - Todos os grupos são válidos")
    
    # 5. TICKET_CHANGES → TICKETS
    print("\n📊 5. Ticket_Changes → Tickets")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.ticket_changes tc
        LEFT JOIN dtic.tickets t ON tc.ticket_id = t.id
        WHERE t.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} ticket_changes órfãos")
        print(f"  ❌ {result.orphans} changes órfãs")
    else:
        print(f"  ✅ OK - Todos os changes têm ticket válido")
    
    # 6. ENTITIES - Hierarquia
    print("\n📊 6. Entities - Hierarquia (entities_id → id)")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_entities e1
        LEFT JOIN dtic.glpi_entities e2 ON e1.entities_id = e2.id
        WHERE e1.entities_id IS NOT NULL AND e2.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} entities órfãs (parent inválido)")
        print(f"  ❌ {result.orphans} entities com parent inválido")
    else:
        print(f"  ✅ OK - Hierarquia de entities consistente")
    
    # 7. LOCATIONS - Hierarquia
    print("\n📊 7. Locations - Hierarquia (parent_id → id)")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_locations l1
        LEFT JOIN dtic.glpi_locations l2 ON l1.parent_id = l2.id
        WHERE l1.parent_id IS NOT NULL AND l2.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} locations órfãs (parent inválido)")
        print(f"  ❌ {result.orphans} locations com parent inválido")
    else:
        print(f"  ✅ OK - Hierarquia de locations consistente")
    
    # 8. CATEGORIES - Hierarquia
    print("\n📊 8. Categories - Hierarquia (parent_id → id)")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_itilcategories c1
        LEFT JOIN dtic.glpi_itilcategories c2 ON c1.parent_id = c2.id
        WHERE c1.parent_id IS NOT NULL AND c2.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} categories órfãs (parent inválido)")
        print(f"  ❌ {result.orphans} categories com parent inválido")
    else:
        print(f"  ✅ OK - Hierarquia de categories consistente")
    
    # 9. GROUPS_USERS → USERS
    print("\n📊 9. Groups_Users → Users")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_groups_users gu
        LEFT JOIN dtic.glpi_users u ON gu.users_id = u.id
        WHERE u.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} groups_users com users_id inválido")
        print(f"  ❌ {result.orphans} usuários inválidos")
    else:
        print(f"  ✅ OK - Todos os usuários são válidos")
    
    # 10. GROUPS_USERS → GROUPS
    print("\n📊 10. Groups_Users → Groups")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_groups_users gu
        LEFT JOIN dtic.glpi_groups g ON gu.groups_id = g.id
        WHERE g.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} groups_users com groups_id inválido")
        print(f"  ❌ {result.orphans} grupos inválidos")
    else:
        print(f"  ✅ OK - Todos os grupos são válidos")
    
    # 11. PROFILES_USERS → USERS
    print("\n📊 11. Profiles_Users → Users")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_profiles_users pu
        LEFT JOIN dtic.glpi_users u ON pu.users_id = u.id
        WHERE u.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} profiles_users com users_id inválido")
        print(f"  ❌ {result.orphans} usuários inválidos")
    else:
        print(f"  ✅ OK - Todos os usuários são válidos")
    
    # 12. PROFILES_USERS → PROFILES
    print("\n📊 12. Profiles_Users → Profiles")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_profiles_users pu
        LEFT JOIN dtic.glpi_profiles p ON pu.profiles_id = p.id
        WHERE p.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} profiles_users com profiles_id inválido")
        print(f"  ❌ {result.orphans} profiles inválidos")
    else:
        print(f"  ✅ OK - Todos os profiles são válidos")
    
    # 13. PROFILES_USERS → ENTITIES
    print("\n📊 13. Profiles_Users → Entities")
    print("-"*80)
    
    result = session.execute(text("""
        SELECT COUNT(*) as orphans
        FROM dtic.glpi_profiles_users pu
        LEFT JOIN dtic.glpi_entities e ON pu.entities_id = e.id
        WHERE e.id IS NULL
    """)).fetchone()
    
    if result.orphans > 0:
        issues.append(f"❌ {result.orphans} profiles_users com entities_id inválido")
        print(f"  ❌ {result.orphans} entities inválidas")
    else:
        print(f"  ✅ OK - Todas as entities são válidas")
    
    return issues, warnings


def check_data_completeness(session):
    """Verifica completude dos dados nas tabelas críticas"""
    print("\n" + "="*80)
    print("COMPLETUDE DE DADOS - TABELAS CRÍTICAS")
    print("="*80)
    
    tables_info = []
    
    # Verificar cada tabela
    tables = [
        ('glpi_users', 'Usuários'),
        ('glpi_profiles', 'Perfis'),
        ('glpi_entities', 'Entidades'),
        ('glpi_groups', 'Grupos'),
        ('glpi_locations', 'Localizações'),
        ('glpi_itilcategories', 'Categorias'),
        ('tickets', 'Tickets'),
    ]
    
    for table, label in tables:
        count = session.execute(text(f'SELECT COUNT(*) FROM dtic.{table}')).scalar()
        tables_info.append((label, count))
        print(f"  {label:20} {count:,} registros")
    
    return tables_info


def main():
    print("\n" + "="*80)
    print("VALIDAÇÃO DE CONSISTÊNCIA - 7 TABELAS CRÍTICAS DTIC")
    print("="*80)
    
    Database._initialize()
    session = Database.get_session()
    
    try:
        # 1. Completude
        tables_info = check_data_completeness(session)
        
        # 2. Integridade Referencial
        issues, warnings = check_referential_integrity(session)
        
        # RELATÓRIO FINAL
        print("\n" + "="*80)
        print("RELATÓRIO FINAL")
        print("="*80)
        
        if not issues and not warnings:
            print("\n✅ PERFEITO! Nenhum problema encontrado!")
            print("\n📊 Todas as 7 tabelas críticas estão:")
            print("   ✓ Consistentes")
            print("   ✓ Com integridade referencial válida")
            print("   ✓ Sem dados órfãos")
            return 0
        
        if issues:
            print("\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS:")
            for issue in issues:
                print(f"   {issue}")
        
        if warnings:
            print("\n⚠️  AVISOS:")
            for warn in warnings:
                print(f"   {warn}")
        
        print("\n📋 AÇÃO NECESSÁRIA:")
        if issues:
            print("   1. Investigar e corrigir problemas de integridade")
            print("   2. Ressincronizar dados se necessário")
        
        return 1 if issues else 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())
