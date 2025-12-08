import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('AskAnalyst')

def build_docker_cmd(project_root, query, openai_base=None, openai_key=None, model_name=None, export=False):
    cmd = [
        'docker','run','--network','bd_cau_v2_app_network',
        '--add-host', 'host.docker.internal:host-gateway',   # Access Host services (NIM)
        '-v', os.path.join(project_root, 'glpi-analysis-cli') + ':/app'
    ]
    if openai_base:
        cmd += ['-e', f'OPENAI_API_BASE={openai_base}']
    if openai_key:
        cmd += ['-e', f'OPENAI_API_KEY={openai_key}']
    if model_name:
        cmd += ['-e', f'LLM_MODEL_NAME={model_name}']

    cmd += ['glpi-analyst']
    if export:
        cmd += ['--export']
    else:
        cmd += [query]
    return cmd

def run_cmd(cmd, log_path):
    logger.info('Running: %s', ' '.join(cmd))
    with open(log_path, 'a', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        for line in proc.stdout:
            sys.stdout.write(line)
            f.write(line)
        proc.wait()
        return proc.returncode

def main():
    parser = argparse.ArgumentParser(description='Enviar uma solicitação de análise ao Analista (PandasAI).')
    parser.add_argument('query', nargs='?', help='Pergunta em linguagem natural (ex.: "Tempo médio de resolução por ano 2023-2025")')
    parser.add_argument('--export', action='store_true', help='Executa a exportação de dados antes da análise')
    parser.add_argument('--openai-base', dest='openai_base', help='Base URL compatível com OpenAI (ex.: http://host.docker.internal:9000/v1)')
    parser.add_argument('--openai-key', dest='openai_key', help='Chave para o endpoint compatível (ex.: NGC_API_KEY)')
    parser.add_argument('--model', dest='model_name', help='Nome do modelo (ex.: meta-llama/llama-3.1-8b-instruct)')
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Load .env from project root
    dotenv_path = os.path.join(project_root, 'glpi-dtic-agent-classificator', '.env')
    load_dotenv(dotenv_path)

    # Defaults from Env if not provided
    openai_base = args.openai_base or os.getenv("LLM_BASE_URL", "http://host.docker.internal:9000/v1")
    openai_key = args.openai_key or os.getenv("LLM_API_KEY", "dummy") 
    model_name = args.model_name or os.getenv("LLM_MODEL_NAME", "meta/llama-3.1-8b-instruct")

    if not args.query and not args.export:
        print('\n📝 Digite sua pergunta para o Analista:')
        q = input('> ').strip()
    else:
        q = args.query or ''

    out_dir = os.path.join(project_root, 'glpi-analysis-cli', 'output')
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(out_dir, f'ask_analyst_{ts}.log')

    # Passo opcional: exportar dados
    if args.export:
        code = run_cmd(build_docker_cmd(project_root, q, openai_base, openai_key, model_name, export=True), log_path)
        if code != 0:
            logger.error('Falha na exportação de dados (código=%s).', code)
            sys.exit(code)

    # Execução da análise
    cmd = build_docker_cmd(project_root, q, openai_base, openai_key, model_name, export=False)
    code = run_cmd(cmd, log_path)
    if code == 0:
        logger.info('Análise concluída. Log salvo em: %s', log_path)
    else:
        logger.error('Falha na análise (código=%s). Log: %s', code, log_path)
    sys.exit(code)

if __name__ == '__main__':
    main()

