
import unittest
import subprocess
import os
import shutil
import sys

# Caminho para o executável CLI
CLI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../_UNIVERSAL_AI_FRAMEWORK/cli.py'))
PYTHON_EXE = sys.executable

class TestCLIRobustness(unittest.TestCase):
    
    def run_cli(self, args):
        """Helper para rodar o CLI e capturar output."""
        cmd = [PYTHON_EXE, CLI_PATH] + args
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            env=os.environ.copy() # Herda env vars atuais
        )
        if result.returncode != 0:
            print(f"\n[DEBUG FAIL] CMD: {cmd}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        return result

    def test_01_help_command(self):
        """Teste se o comando help roda sem erro."""
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("AI-Native Engineering CLI", result.stdout)

    def test_02_init_command(self):
        """Teste se o init cria as pastas corretamente."""
        # Limpeza prévia (perigoso em prod, mas aqui é teste controlado)
        if os.path.exists("docs/specs_test"):
            shutil.rmtree("docs/specs_test")
            
        result = self.run_cli(["init"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Framework pronto para uso", result.stdout)
        
        # Verifica se pastas críticas existem
        self.assertTrue(os.path.exists("docs/specs"))
        self.assertTrue(os.path.exists("tests/integration"))

    def test_03_check_command_success(self):
        """Teste do comando check (assumindo que o ambiente dev atual está ok)."""
        # Este teste depende do ambiente estar configurado. 
        # Como eu acabei de corrigir o pre_flight.py e rodamos manualmente antes, deve passar.
        result = self.run_cli(["check"])
        
        # Se falhar, quero ver o output para saber por quê
        if result.returncode != 0:
            print(f"\n[DEBUG] Check Output:\n{result.stdout}")
            
        self.assertIn("AI-Native Development: Pre-Flight Check", result.stdout)
        # Nota: Pode retornar 1 se o Ollama não estiver rodando, mas o script não deve quebrar (crash).
        # Vamos aceitar returncode 0 ou 1, desde que não seja crash (ex: 255)
        self.assertIn(result.returncode, [0, 1])

    def test_04_spec_generation(self):
        """Teste de geração de spec."""
        feature_name = "test_feature_stress"
        result = self.run_cli(["spec", feature_name])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Spec Template criado", result.stdout)
        
        # Verificar se arquivo foi criado
        # O nome do arquivo tem timestamp, então listamos o diretório
        files = os.listdir("docs/specs")
        found = any(feature_name in f for f in files)
        self.assertTrue(found, "Arquivo de spec não foi encontrado!")

    def test_05_invalid_command(self):
        """Teste de comando inexistente."""
        result = self.run_cli(["fazer_cafe"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_06_check_missing_env(self):
        """Simula falta de .env para ver se o check trata o erro."""
        # Renomeia .env temporariamente
        if os.path.exists(".env"):
            os.rename(".env", ".env.bak")
        
        try:
            result = self.run_cli(["check"])
            self.assertIn(".env file not found", result.stdout)
            self.assertNotEqual(result.returncode, 0) # Deve falhar
        finally:
            # Restaura .env
            if os.path.exists(".env.bak"):
                os.rename(".env.bak", ".env")

if __name__ == '__main__':
    unittest.main()
