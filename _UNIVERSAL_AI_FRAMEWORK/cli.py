
import argparse
import sys
import os
from scripts.pre_flight import run_checks
from scripts.spec_generator import create_spec_template

def main():
    parser = argparse.ArgumentParser(description="AI-Native Engineering CLI - Governança e Automação para Dev com IA")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: init
    parser_init = subparsers.add_parser("init", help="Inicializa o framework no projeto atual")

    # Comando: check (Pre-flight)
    parser_check = subparsers.add_parser("check", help="Executa verificação de ambiente (DB, Docker, LLM)")

    # Comando: spec
    parser_spec = subparsers.add_parser("spec", help="Cria um novo template de especificação técnica")
    parser_spec.add_argument("name", help="Nome da funcionalidade (ex: login_auth)")

    args = parser.parse_args()

    if args.command == "init":
        print("[INFO] Inicializando AI-Framework...")
        # Lógica de init (criar pastas se não existirem)
        dirs = ["docs/specs", "tests/integration", ".ai/prompts"]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            print(f"   [OK] Diretório criado: {d}")
        print("[DONE] Framework pronto para uso.")

    elif args.command == "check":
        print("[INFO] Executando Pre-Flight Checks...")
        try:
            run_checks()
        except SystemExit as e:
            sys.exit(e.code)

    elif args.command == "spec":
        create_spec_template(args.name)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
