#!/bin/bash

# Fine-Tuning com NVIDIA RTX A 4000
# 16GB VRAM - Otimizado para LoRA

set -e

echo "🚀 NVIDIA Fine-Tuning Pipeline - RTX A 4000"
echo "============================================"
echo ""

# Verificar GPU
echo "📊 GPU Info:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# Config
MODEL_SIZE=${1:-"7b"}
METHOD=${2:-"lora"}
DATA_FILE="training_data.jsonl"
OUTPUT_DIR="./fine_tuned_models"

echo "⚙️  Config:"
echo "  Model: llama-${MODEL_SIZE}"
echo "  Method: ${METHOD}"
echo "  Data: ${DATA_FILE}"
echo ""

# Verificar dados
if [ ! -f "$DATA_FILE" ]; then
    echo "❌ Dados não encontrados. Execute:"
    echo "   npx tsx scripts/export_for_finetuning.ts"
    exit 1
fi

EXAMPLES=$(wc -l < "$DATA_FILE")
echo "📝 Training examples: $EXAMPLES"
echo ""

# Fine-tuning com TensorRT-LLM (NVIDIA)
if python3 -c "import tensorrt_llm" 2>/dev/null; then
    echo "🎯 Using TensorRT-LLM (NVIDIA optimized)"
    python3 ./scripts/finetune_tensorrt.py \
        --model-size "${MODEL_SIZE}" \
        --data "${DATA_FILE}" \
        --output "${OUTPUT_DIR}"
else
    echo "⚠️  TensorRT-LLM not found. Using Ollama..."
    
    # Fallback: Ollama
    ollama create glpi-agent-finetuned -f Modelfile
fi

echo ""
echo "✅ Fine-tuning completo!"
echo "   Modelo: ${OUTPUT_DIR}/glpi-agent-finetuned"
