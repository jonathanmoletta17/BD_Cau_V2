"""
Script de Limpeza Automática - Remove scripts não essenciais
=============================================================

Remove 15-16 scripts de teste/debug/validação mantendo apenas os essenciais.
"""
import os
import shutil
from pathlib import Path

# Scripts para DELETAR
SCRIPTS_TO_DELETE = [
    # Teste/Debug (11)
    'truncate_dtic.py',
    'validate_corrections.py',
    'validate_entities.py',
    'validate_entities.sql',
    'quick_check.py',
    'validate_sync_results.py',
    'audit_data_quality.py',
    'audit_db.py',
    'diagnose_categories.py',
    'probe_glpi_types.py',
    'seed_validation_data.py',
    
    # Duplicado/Obsoleto (4)
    'rebuild_database.py',
    'drop_tables.py',
    'setup-postgres-docker.ps1',
    'run_dev.ps1',
    
    # Verificar se é usado
    'setup_helpers.py',
]

def main():
    scripts_dir = Path(__file__).parent
    backup_dir = scripts_dir.parent / 'scripts_backup'
    
    print("\n" + "="*60)
    print("LIMPEZA DE SCRIPTS NÃO ESSENCIAIS")
    print("="*60)
    
    # Criar backup
    backup_dir.mkdir(exist_ok=True)
    print(f"\nBackup: {backup_dir}")
    
    deleted_count = 0
    not_found = []
    
    for script in SCRIPTS_TO_DELETE:
        script_path = scripts_dir / script
        
        if script_path.exists():
            # Mover para backup
            backup_path = backup_dir / script
            shutil.move(str(script_path), str(backup_path))
            print(f"  [OK] Movido para backup: {script}")
            deleted_count += 1
        else:
            not_found.append(script)
    
    print(f"\n{'='*60}")
    print(f"RESULTADO:")
    print(f"  - Movidos para backup: {deleted_count}")
    if not_found:
        print(f"  - Não encontrados: {len(not_found)}")
        for nf in not_found:
            print(f"      {nf}")
    
    # Listar o que sobrou
    remaining = [f.name for f in scripts_dir.iterdir() 
                 if f.is_file() and f.suffix in ['.py', '.sh', '.ps1', '.md', '.sql']]
    
    print(f"\n{'='*60}")
    print("SCRIPTS RESTANTES (ESSENCIAIS):")
    for r in sorted(remaining):
        print(f"  ✅ {r}")
    
    print(f"\n{'='*60}")
    print("LIMPEZA CONCLUÍDA!")
    print(f"{'='*60}\n")
    print(f"Backup salvo em: {backup_dir}")
    print("Para restaurar, copie de volta da pasta scripts_backup")


if __name__ == '__main__':
    main()
