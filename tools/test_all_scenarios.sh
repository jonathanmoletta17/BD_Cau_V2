#!/bin/bash
# Script de Teste Completo - 4 Cenários Originais
# Valida correções das 5 fases TOD

API="http://localhost:4000/chat"
HEADERS='-H "Content-Type: application/json"'

echo "======================================================================"
echo "TESTES ORIGINAIS - Validação Completa das Correções TOD"
echo "======================================================================"
echo ""

# ======================================================================
# TESTE 1: Impressora (deve continuar funcionando perfeitamente)
# ======================================================================
echo "📝 TESTE 1: IMPRESSORA COM ERRO"
echo "----------------------------------------------------------------------"
echo "Cenário: User fornece todas informações de uma vez"
echo ""

MSG1='{"message":"IMPRESSORA COM ERRO, SOU DO RH, ANDAR TERREO SALA DO FUNDO, MEU RAMAL É 4121"}'
RESP1=$(curl -s -X POST $API $HEADERS -d "$MSG1")
CONV1=$(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('conversationId', 'ERROR'))")

echo "Resposta Bot: $(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:100])")"
echo "Estado: $(echo $RESP1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Complete={d['state']['isComplete']}, Missing={d['state']['missingSlots']}\")")"
echo ""

sleep 2

MSG2="{\"message\":\"SIM\",\"conversationId\":\"$CONV1\"}"
RESP2=$(curl -s -X POST $API $HEADERS -d "$MSG2")

echo "Após confirmação:"
echo "Resposta: $(echo $RESP2 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
echo "Ticket criado: $(echo $RESP2 | python3 -c "import sys,json; print('Sim' if json.load(sys.stdin).get('ticketId') else 'Não')")"
echo ""

if echo $RESP2 | python3 -c "import sys,json; exit(0 if json.load(sys.stdin).get('ticketId') else 1)"; then
    echo "✅ TESTE 1: PASSOU"
else
    echo "❌ TESTE 1: FALHOU"
fi

echo ""
echo "======================================================================"
echo ""

# ======================================================================
# TESTE 2: Criar Usuário (deve resolver loop infinito de jobTitle)
# ======================================================================
echo "📝 TESTE 2: CRIAR USUARIO NOVO ESTAGIARIO"
echo "----------------------------------------------------------------------"
echo "Cenário: Testar que aceita valores após 3 tentativas"
echo ""

MSG1='{"message":"CRIAR USUARIO PARA NOVO ESTAGIARIO"}'
RESP1=$(curl -s -X POST $API $HEADERS -d "$MSG1")
CONV2=$(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('conversationId', 'ERROR'))")

echo "Bot pergunta: $(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
sleep 1

# Fornecer informações progressivamente
MSG2="{\"message\":\"JONATHAN MOLETTA\",\"conversationId\":\"$CONV2\"}"
RESP2=$(curl -s -X POST $API $HEADERS -d "$MSG2")
echo "Nome fornecido, bot pergunta: $(echo $RESP2 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:60])")"
sleep 1

MSG3="{\"message\":\"Casa Civil\",\"conversationId\":\"$CONV2\"}"
RESP3=$(curl -s -X POST $API $HEADERS -d "$MSG3")
echo "Org fornecida, bot pergunta: $(echo $RESP3 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:60])")"
sleep 1

# Testar tentativas de jobTitle (deve aceitar após 3x)
MSG4="{\"message\":\"tecnico\",\"conversationId\":\"$CONV2\"}"
RESP4=$(curl -s -X POST $API $HEADERS -d "$MSG4")
echo "JobTitle tent. 1: $(echo $RESP4 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:60])")"
sleep 1

MSG5="{\"message\":\"ti\",\"conversationId\":\"$CONV2\"}"
RESP5=$(curl -s -X POST $API $HEADERS -d "$MSG5")
echo "JobTitle tent. 2: $(echo $RESP5 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:60])")"
sleep 1

MSG6="{\"message\":\"trabalho com computador\",\"conversationId\":\"$CONV2\"}"
RESP6=$(curl -s -X POST $API $HEADERS -d "$MSG6")
echo "JobTitle tent. 3 (deve aceitar): $(echo $RESP6 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
echo ""

# Verificar se progrediu (não ficou em loop)
MISSING_COUNT=$(echo $RESP6 | python3 -c "import sys,json; print(len(json.load(sys.stdin)['state']['missingSlots']))")

if [ "$MISSING_COUNT" -lt 8 ]; then
    echo "✅ TESTE 2: PASSOU (progrediu, não ficou em loop)"
else
    echo "❌ TESTE 2: FALHOU (ainda em loop)"
fi

echo ""
echo "======================================================================"
echo ""

# ======================================================================
# TESTE 3: Notebook (deve resolver Casa Amarela e confirmação)
# ======================================================================
echo "📝 TESTE 3: PEDIR NOTEBOOK HOME OFFICE"
echo "----------------------------------------------------------------------"
echo "Cenário: Casa Amarela não deve virar 'sua casa'"
echo ""

MSG1='{"message":"preciso pedir um notebook para colega que vai ficar de home office"}'
RESP1=$(curl -s -X POST $API $HEADERS -d "$MSG1")
CONV3=$(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('conversationId', 'ERROR'))")

echo "Bot pergunta: $(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
sleep 1

MSG2="{\"message\":\"é na casa amarela, sala do compras e pat\",\"conversationId\":\"$CONV3\"}"
RESP2=$(curl -s -X POST $API $HEADERS -d "$MSG2")
echo "Location fornecido: $(echo $RESP2 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
sleep 1

MSG3="{\"message\":\"4121\",\"conversationId\":\"$CONV3\"}"
RESP3=$(curl -s -X POST $API $HEADERS -d "$MSG3")
CONFIRM_MSG=$(echo $RESP3 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])")
echo "Confirmação: $CONFIRM_MSG"
echo ""

# Verificar se NÃO tem "sua casa"
if echo "$CONFIRM_MSG" | grep -iq "sua casa"; then
    echo "❌ TESTE 3: FALHOU (ainda diz 'sua casa')"
else
    echo "✅ TESTE 3: PASSOU (não confunde Casa Amarela com residência)"
fi

echo ""
echo "======================================================================"
echo ""

# ======================================================================
# TESTE 4: Túnel VPN (deve continuar funcionando)
# ======================================================================
echo "📝 TESTE 4: ACESSO TUNEL VPN"
echo "----------------------------------------------------------------------"
echo "Cenário: Fornece tudo de uma vez e confirma"
echo ""

MSG1='{"message":"preciso de acesso ao tunel para trabalho home"}'
RESP1=$(curl -s -X POST $API $HEADERS -d "$MSG1")
CONV4=$(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('conversationId', 'ERROR'))")

echo "Bot pergunta: $(echo $RESP1 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
sleep 1

MSG2="{\"message\":\"to da casa amarela 1005, na sala da dtic, meu ramal é 4221\",\"conversationId\":\"$CONV4\"}"
RESP2=$(curl -s -X POST $API $HEADERS -d "$MSG2")
echo "Confirmação: $(echo $RESP2 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:100])")"
sleep 1

MSG3="{\"message\":\"sim\",\"conversationId\":\"$CONV4\"}"
RESP3=$(curl -s -X POST $API $HEADERS -d "$MSG3")

echo "Após sim:"
echo "Resposta: $(echo $RESP3 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:80])")"
echo "Ticket: $(echo $RESP3 | python3 -c "import sys,json; print('Criado' if json.load(sys.stdin).get('ticketId') else 'Não criado')")"
echo ""

if echo $RESP3 | python3 -c "import sys,json; exit(0 if json.load(sys.stdin).get('ticketId') else 1)"; then
    echo "✅ TESTE 4: PASSOU"
else
    echo "❌ TESTE 4: FALHOU"
fi

echo ""
echo "======================================================================"
echo "RESUMO DOS TESTES"
echo "======================================================================"
echo ""
echo "Valide os resultados acima:"
echo "- TESTE 1 (Impressora): Deve ter criado ticket"
echo "- TESTE 2 (Criar Usuário): Deve ter progredido (não loop)"
echo "- TESTE 3 (Notebook): Não deve ter 'sua casa'"
echo "- TESTE 4 (Túnel): Deve ter criado ticket"
echo ""
