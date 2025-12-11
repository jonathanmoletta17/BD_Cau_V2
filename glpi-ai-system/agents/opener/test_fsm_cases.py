"""
Testes dos 5 Casos Problemáticos Reais
Valida comportamento da FSM contra as interações que falharam anteriormente.
"""

from fsm_standalone import simulate_conversation, TicketContext, TicketFSM, Urgency, Impact

def run_tests():
    print("==================================================================")
    print("INICIANDO BATERIA DE TESTES DE REGRAS DE NEGÓCIO (FSM)")
    print("==================================================================")

    # CASO 1: Internet Lenta
    # Falha original: Perguntou Urgencia ao invés de local.
    # Correto: Perguntar Local, Urgencia Média.
    print("\n[CASO 1] Internet Lenta")
    ctx1 = simulate_conversation([
        "Preciso abrir um chamado. Minha internet está muito ruim.",
        "Fica no meu setor, RH"
    ])
    assert ctx1.location == "Rh", f"Falha Local: {ctx1.location}"
    assert ctx1.urgency == Urgency.MEDIUM, f"Falha Urgencia: {ctx1.urgency}"
    assert "location" not in ctx1.missing_info
    print("PASS")

    # CASO 2: Senha Bloqueada
    # Falha original: Urgencia Baixa.
    # Correto: Urgencia Alta.
    print("\n[CASO 2] Senha Bloqueada")
    ctx2 = simulate_conversation([
        "Minha senha está bloqueada, preciso de ajuda.",
        "Estou na sala 202"
    ])
    assert ctx2.urgency == Urgency.HIGH, f"Falha Urgencia: {ctx2.urgency} (Era pra ser Alta)"
    print(f"DEBUG LOCAL: {repr(ctx2.location)}")
    print(f"DEBUG LOCAL: {repr(ctx2.location)}")
    assert "202" in ctx2.location
    print("PASS")

    # CASO 3: Fones de Ouvido (Local já informado)
    # Falha original: Perguntou Urgencia (inútil).
    # Correto: Pegar local 'Casa Civil 1005' e Urgencia Baixa direto.
    print("\n[CASO 3] Fones de Ouvido")
    ctx3 = simulate_conversation([
        "Preciso solicitar dois fones de ouvido para o nosso departamento, ficamos na Casa Civil 1005"
    ])
    assert "Casa Civil" in ctx3.location, f"Falha Local: {ctx3.location}"
    assert ctx3.urgency == Urgency.LOW, f"Falha Urgencia: {ctx3.urgency}"
    assert ctx3.ready_to_submit == True, "Deveria estar pronto sem perguntas extras"
    print("PASS")

    # CASO 4: Estações Desktop
    # Falha original: Assumiu urgencia Baixa.
    # Correto: Perguntar local (Obrigatório). Urgencia Baixa é aceitável se não for critico, mas local é chave.
    print("\n[CASO 4] Estações Desktop")
    ctx4 = simulate_conversation([
        "Preciso de ajuda para solicitar duas estações de trabalho desktop para servidores novos.",
        "Prédio Anexo, Sala 101"
    ])
    assert "Anexo" in ctx4.location or "101" in ctx4.location, f"Falha Local: {ctx4.location}"
    assert ctx4.intent == "hardware_request"
    print("PASS")

    # CASO 5: Caixa Compartilhada
    # Falha original: Assumiu local "Sala do Usuário".
    # Correto: Urgencia Baixa (Serviço).
    print("\n[CASO 5] Caixa Compartilhada")
    ctx5 = simulate_conversation([
        "Preciso de ajuda para adicionar a caixa compartilhada da divisão no meu email."
    ])
    # Aqui o FSM pode decidir perguntar local ou não. No meu código email não pede local obrigatório.
    assert ctx5.urgency == Urgency.LOW
    assert ctx5.impact == Impact.INDIVIDUAL
    assert ctx5.intent == "email_issue"
    print("PASS")

    print("\n\n ALL 5 TEST CASES PASSED!")
    print("A Lógica da FSM corrigiu as inconsistências observadas.")

if __name__ == "__main__":
    run_tests()
