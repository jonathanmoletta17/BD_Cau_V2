#!/bin/bash

# Configuration
API_URL="http://localhost:4000"
USERNAME="jonathan-moletta"
PASSWORD="JNMolett@#2025"

echo "==================================================="
echo "🚀 INICIANDO SIMULAÇÃO COMPLETA DO SISTEMA (Full Flow)"
echo "==================================================="

# 1. Authentication
echo -e "\n🔹 1. Testando Autenticação..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

USER_ID=$(echo $LOGIN_RESPONSE | grep -o '"userId":[0-9]*' | grep -o '[0-9]*')
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$USER_ID" ]; then
  echo "❌ Falha no Login!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login Sucesso! UserID: $USER_ID"

# 2. Chat Flow - Standard Ticket Creation
echo -e "\n🔹 2. Testando Fluxo de Criação de Ticket (Fones de Ouvido)..."
CONV_ID="test-flow-$(date +%s)"

# 2.1 Initial Request
echo "   📤 User: 'Preciso solicitação 3 fones de ouvido'"
RESP1=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Preciso solicitação 3 fones de ouvido\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID\"}")
echo "   📥 Agent: $(echo $RESP1 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"

# 2.2 Provide Info
echo "   📤 User: 'Estou no RH, 3 andar casa civil, ramal 4121'"
RESP2=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Estou no RH, 3 andar casa civil, ramal 4121\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID\"}")
echo "   📥 Agent: $(echo $RESP2 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"

# 2.3 Confirm
echo "   📤 User: 'Sim'"
RESP3=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Sim\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID\"}")

TICKET_ID=$(echo $RESP3 | grep -o '"ticketId":[0-9]*' | grep -o '[0-9]*')
echo "   📥 Agent: $(echo $RESP3 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"

if [ ! -z "$TICKET_ID" ]; then
  echo "   ✅ Ticket Criado com Sucesso! ID: $TICKET_ID"
else
  echo "   ❌ Falha ao criar ticket."
  echo "   Full Response: $RESP3"
  exit 1
fi

# 3. Post-Ticket Loop Check
echo -e "\n🔹 3. Testando Reset de Estado (Loop do Obrigado)..."
echo "   📤 User: 'Obrigado'"
RESP4=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Obrigado\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID\"}")

RESPONSE_TEXT=$(echo $RESP4 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)
echo "   📥 Agent: $RESPONSE_TEXT"

# Check if agent tries to create another ticket (look for confirmation keywords)
if [[ "$RESPONSE_TEXT" == *"ticket"* ]] || [[ "$RESPONSE_TEXT" == *"confirmar"* ]]; then
    echo "   ❌ FALHA: Agente tentou criar ticket novamente! (Loop Infinito Detectado)"
else
    echo "   ✅ SUCESSO: Agente respondeu adequadamente sem tentar recriar ticket."
fi

# 4. Context Switching Check
echo -e "\n🔹 4. Testando Mudança de Contexto (Context Switch)..."
CONV_ID_2="test-switch-$(date +%s)"

# 4.1 Start with Printer
echo "   📤 User: 'Minha impressora HP parou de funcionar'"
RESP5=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Minha impressora HP parou de funcionar\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID_2\"}")
echo "   📥 Agent: $(echo $RESP5 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"
# Check internal state via logs (optional, but assumed working based on previous verification)

# 4.2 Switch to VPN
echo "   📤 User: 'Esquece a impressora, preciso de acesso VPN'"
RESP6=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Esquece a impressora, preciso de acesso VPN\", \"userId\": \"$USER_ID\", \"conversationId\": \"$CONV_ID_2\"}")
echo "   📥 Agent: $(echo $RESP6 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"

# Check if response mentions VPN
RESPONSE_TEXT_VPN=$(echo $RESP6 | grep -o '"response":"[^"]*"' | cut -d'"' -f4)
if [[ "$RESPONSE_TEXT_VPN" == *"VPN"* ]]; then
    echo "   ✅ SUCESSO: Agente mudou contexto para VPN."
else
    echo "   ❌ FALHA: Agente não detectou mudança para VPN adequadamente."
fi

echo -e "\n==================================================="
echo "🏁 SIMULAÇÃO CONCLUÍDA"
echo "==================================================="
