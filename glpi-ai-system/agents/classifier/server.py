from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
import time
import os

from agents.classifier.daemon import ClassifierDaemon
from agents.classifier.schemas import ClassificationInput, ClassificationResult

daemon_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global daemon_instance
    print("🚀 Iniciando Servidor API & Daemon Classificador...")
    
    # 1. Carrega o Daemon (e o modelo pesado)
    daemon_instance = ClassifierDaemon()
    
    # 2. Inicia o loop de background em uma thread separada
    # daemon=True garante que a thread morre se o processo principal morrer
    loop_thread = threading.Thread(target=daemon_instance.run_loop, args=(30,), daemon=True)
    loop_thread.start()
    print("✅ Background Loop Iniciado.")
    
    yield
    
    print("🛑 Encerrando Servidor...")

app = FastAPI(lifespan=lifespan, title="GLPI Classifier API")

@app.get("/health")
def health():
    return {"status": "ok", "loaded": daemon_instance is not None}

@app.post("/predict", response_model=ClassificationResult)
def predict(data: ClassificationInput):
    """
    Endpoint síncrono para classificar texto sob demanda.
    Usa a mesma instância de agente carregada pelo daemon.
    """
    if not daemon_instance:
        return {"error": "Daemon not ready"}
        
    print(f"📡 API Request: Classificando '{data.summary}'")
    result = daemon_instance.agent.classify(data)
    return result
