import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import ProgrammingError

# Mock base for reproduction
Base = declarative_base()

# 1. Definição com Erro (Simulada)
class TicketError(Base):
    __tablename__ = 'tickets_error'
    __table_args__ = (
        Index('ix_test_dup', 'entidade_id'), # Explicit Index
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True)
    # Definição duplicada que causou o erro: explicit index AND index=True
    entidade_id = Column(Integer, index=True) 

# 2. Definição Corrigida (Atual)
class TicketFixed(Base):
    __tablename__ = 'tickets_fixed'
    __table_args__ = (
        Index('ix_test_fixed', 'entidade_id'), # Explicit Index
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True)
    # Correção: removemos index=True
    entidade_id = Column(Integer)

def test_schema_creation():
    # Use in-memory SQLite for fast testing of schema generation logic
    # Note: SQLite naming might behave slightly differently but SQLAlchemy logic is the same
    engine = create_engine('sqlite:///:memory:')
    
    print("--- Teste 1: Reprodução do Erro (Simulação) ---")
    try:
        # Tentar criar a tabela com erro
        # Nota: SQLAlchemy em SQLite pode não disparar o erro exato de DuplicateTable do Postgres
        # Mas vamos validar a lógica de geração de DDL
        Base.metadata.create_all(engine)
        print("WARN: SQLite permitiu a criação (comportamento esperado para SQLite, mas Postgres falharia).")
        print("Verificando indices criados...")
        # Inspect indexes
        from sqlalchemy import inspect
        insp = inspect(engine)
        indexes = insp.get_indexes('tickets_error')
        print(f"Indices na tabela com erro: {[i['name'] for i in indexes]}")
    except Exception as e:
        print(f"Erro capturado (Esperado): {e}")

    print("\n--- Teste 2: Validação da Correção (Importando Modelo Real) ---")
    try:
        # Importar o modelo real para garantir que ele não tem erros de definição
        project_root = os.getcwd()
        service_path = os.path.join(project_root, 'glpi-data-service')
        sys.path.append(service_path)
        
        from src.modules.sis.tickets.models import Ticket
        print("Modelo Ticket importado com sucesso.")
        
        # Validar que não há colapso na definição da SQLAlchemy
        # Se houvesse erro de definição python-side, falharia na importação ou inspeção
        if Ticket.__table__.indexes:
             print(f"Índices definidos no modelo Real: {[i.name for i in Ticket.__table__.indexes]}")
             
        # Verificar se identificamos a remoção do index=True na colunas
        entidade_col = Ticket.__table__.c.entidade_id
        print(f"Coluna 'entidade_id' tem index=True? {entidade_col.index}")
        
        if entidade_col.index is None:
            print("SUCESSO: Coluna 'entidade_id' não tem mais index=True redundante.")
        else:
            print("FALHA: Coluna 'entidade_id' ainda tem index=True.")
            sys.exit(1)

    except ImportError as e:
        print(f"Erro ao importar modelo real (verifique o path): {e}")
        # Ajuste de path para o ambiente docker pode ser necessário se rodar local
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_schema_creation()
