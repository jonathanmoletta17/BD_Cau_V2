# 18 — Detalhamento: RESET_PASSWORD

Baseado em evidências empíricas (~11.000 tickets analisados), definimos a regra padrão para reset de senhas.

---

## 1. O Cenário dos Dados
- **~71%** dos tickets de senha referem-se a **Rede / Windows / AD**.
- **~14%** referem-se a Office 365 / E-mail.
- O restante é difuso.

**Conclusão:** "Reset de senha" no contexto do órgão é, esmagadoramente, **Senha de Rede (AD)**.

---

## 2. Regra Invariante (Padrão de Inferência)

**Em pedidos genéricos** (ex: "esqueci minha senha", "não logo", "bloqueou"):
1. O agente deve **assumir como padrão** que se trata de `Rede/Windows` (Active Directory).
2. O agente **não deve perguntar** "Qual senha?" se não houver ambiguidade explícita.
3. O agente deve **comunicar a suposição** na resposta/confirmação (ex: "Entendido, vou abrir um chamado para reset da sua senha de REDE").

**Exceções (Override):**
- Se o usuário mencionar explicitamente: "Office 365", "Outlook", "E-mail", "2FA", "MFA", "Token".
- Nestes casos, o agente segue o fluxo específico ou classifica o sistema afetado de acordo.

---

## 3. Justificativa
- **Risco de errar assumindo AD:** Baixo (~30%).
- **Custo de perguntar sempre:** Alto e gera atrito desnecessário em 70% dos casos.
- **Correção:** O usuário pode corrigir na confirmação ("Não, é do e-mail").
