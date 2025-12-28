# NIM Integration - Manual Testing Guide

## Prerequisites
- Docker and docker-compose installed
- NGC API Key configured in `.env`

## Test 1: Starting the Stack

```bash
# Navigate to project root
cd /home/workbench/projects/BD_Cau_V2

# Start NIM and Backend
docker-compose up -d nim-llm redis ollama backend

# Monitor logs
docker-compose logs -f nim-llm backend
```

**Expected**:
- NIM should start (may take 2-3 minutes for first model download)
- Backend logs should show: `[Config] LLM Providers: NIM: http://nim-llm:8000`
- Backend should become healthy

---

## Test 2: Check LLM Status Endpoint

```bash
curl http://localhost:4000/llm-status
```

**Expected Response**:
```json
{
  "primaryProvider": "NIM",
  "circuitState": "CLOSED",
  "fallbackEnabled": true,
  "consecutiveNimSuccesses": 0,
  "timestamp": "2025-12-23T09:10:00.000Z"
}
```

---

## Test 3: Test NIM Directly

```bash
curl -X POST http://localhost:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Oi"}],
    "max_tokens": 50
  }'
```

**Expected**: JSON response with generated text

---

## Test 4: Test Through Agent (NIM)

```bash
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Criar usuário João da SECOM",
    "sessionId": "test-nim-1"
  }'
```

**Backend Logs - Expected**:
```
[LLMService] Calling http://nim-llm:8000/v1/chat/completions with model meta/llama-3.1-8b-instruct
[LLMService] ✅ NIM successful (850ms)
[V4] Decisão do Router: SERVICE_REQUEST
```

**Response**: Should return a form for creating user

---

## Test 5: Test Fallback (NIM Down)

```bash
# Stop NIM
docker stop glpi-nim

# Test again
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Impressora não funciona",
    "sessionId": "test-fallback-1"
  }'
```

**Backend Logs - Expected**:
```
[LLMService] ❌ NIM failed: fetch failed
[LLMService] 🔄 Falling back to Ollama...
[LLMService] Calling http://ollama:11434/v1/chat/completions
[LLMService] ✅ Ollama fallback successful (1200ms)
```

**Response**: Should still classify correctly using Ollama

---

## Test 6: Circuit Breaker Behavior

```bash
# With NIM still down, make 3 more requests
for i in {1..3}; do
  curl -X POST http://localhost:4000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"Test $i\",\"sessionId\":\"circuit-test-$i\"}"
  echo ""
done

# Check LLM status
curl http://localhost:4000/llm-status
```

**Expected Response** (after 3 failures):
```json
{
  "primaryProvider": "NIM",
  "circuitState": "OPEN",  // ← Circuit opened!
  "fallbackEnabled": true,
  "consecutiveNimSuccesses": 0
}
```

**Backend Logs - Expected**:
``` [CircuitBreaker] Failure recorded (1/3)
[CircuitBreaker] Failure recorded (2/3)
[CircuitBreaker] Failure recorded (3/3)
[CircuitBreaker] Failure threshold reached, opening circuit for 300s
[LLMService] ⚠️ Circuit OPEN, using Ollama directly
```

**Next Request**: Should not even attempt NIM, goes straight to Ollama

---

## Test 7: Circuit Recovery

```bash
# Restart NIM
docker start glpi-nim

# Wait 5 minutes (circuit recovery timeout) OR manually reset:
curl -X POST http://localhost:4000/admin/reset-circuit

# Make a request
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Teste de recuperação",
    "sessionId": "recovery-test"
  }'
```

**Expected**:
```
[CircuitBreaker] Recovery timeout passed, entering HALF_OPEN state
[LLMService] Calling http://nim-llm:8000/v1/chat/completions
[LLMService] ✅ NIM successful (900ms)
[CircuitBreaker] Success in HALF_OPEN (1/2)
```

After 2 consecutive successes:
```
[CircuitBreaker] Provider recovered, closing circuit
```

---

## Test 8: Latency Comparison

```bash
# Benchmark script
for i in {1..10}; do
  echo "Request $i:"
  time curl -s -X POST http://localhost:4000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"Criar usuário Test$i\",\"sessionId\":\"bench-$i\"}" \
    > /dev/null
  echo ""
done
```

**Expected Latencies**:
- **NIM**: 500-1500ms (first call may be slower)
- **Ollama**: 1000-3000ms

---

## Test 9: Multi-Turn Conversation

```bash
# First turn
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Impressora HP não imprime",
    "sessionId": "printer-issue",
    "conversationId": "conv-printer-123"
  }'

# Second turn (respond to agent's question)
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Papel preso",
    "sessionId": "printer-issue",
    "conversationId": "conv-printer-123"
  }'
```

**Expected**: Agent should make follow-up diagnostic questions

---

## Troubleshooting

### NIM Not Starting
```bash
# Check NGC API Key
docker exec glpi-nim env | grep NGC_API_KEY

# Check GPU availability
nvidia-smi

# Check NIM logs
docker logs glpi-nim --tail 100
```

### Circuit Stuck OPEN
```bash
# Reset manually (if you add admin endpoint)
curl -X POST http://localhost:4000/admin/reset-circuit

# Or restart backend
docker restart glpi-backend
```

### High Latency
```bash
# Check if model is cached
docker exec glpi-nim ls -lh /opt/nim/.cache

# Monitor GPU usage
watch -n 1 nvidia-smi
```

---

## Success Criteria

✅ NIM responds in <2s after warm-up
✅ Fallback to Ollama works automatically
✅ Circuit breaker opens after 3 failures
✅ Circuit recovers after timeout
✅ `/llm-status` endpoint shows correct state
✅ Multi-turn conversations maintain context
