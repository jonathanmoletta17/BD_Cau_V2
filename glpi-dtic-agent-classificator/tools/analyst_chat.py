import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('AnalystChat')

def docker_run(query, openai_base=None, openai_key=None, model_name=None):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cmd = [
        'docker','run','--network','bd_cau_v2_app_network',
        '-v', os.path.join(project_root, 'glpi-analysis-cli') + ':/app'
    ]
    if openai_base:
        cmd += ['-e', f'OPENAI_API_BASE={openai_base}']
    if openai_key:
        cmd += ['-e', f'OPENAI_API_KEY={openai_key}']
    if model_name:
        cmd += ['-e', f'LLM_MODEL_NAME={model_name}']
    cmd += ['glpi-analyst', query]
    return cmd

def run(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    for line in proc.stdout:
        sys.stdout.write(line)
    return proc.wait()

def main():
    parser = argparse.ArgumentParser(description='Chat CMD com o Analista (dados GLPI via PandasAI).')
    parser.add_argument('--openai-base', help='Base URL OpenAI-compatible (ex.: http://host.docker.internal:9000/v1)')
    parser.add_argument('--openai-key', help='Chave do endpoint (ex.: NGC_API_KEY)')
    parser.add_argument('--model', help='Nome do modelo (ex.: meta-llama/llama-3.1-8b-instruct)')
    args = parser.parse_args()

    print("Bem-vindo ao Analyst Chat (digite 'sair' para encerrar)")
    while True:
        try:
            q = input("Analyst > ").strip()
        except KeyboardInterrupt:
            print("\nEncerrado.")
            break
        if not q:
            continue
        if q.lower() in ["sair","exit","quit"]:
            break

        cmd = docker_run(q, args.openai_base, args.openai_key, args.model)
        rc = run(cmd)
        if rc != 0:
            logger.error('Falha ao processar a consulta (código=%s).', rc)

if __name__ == '__main__':
    main()

