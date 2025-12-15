# Estratégia de Testes para Desenvolvimento Assistido por IA

## A Pirâmide de Testes da IA

Ao usar IA para gerar código, a pirâmide de testes muda ligeiramente de foco. Como a IA pode gerar lógica sintaticamente correta mas semanticamente errada (alucinação), precisamos reforçar a base.

### 1. Testes de Unidade (Lógica Pura)
*   **O que testar:** Funções matemáticas, transformações de strings, regras de negócio isoladas.
*   **Ferramenta:** `pytest`
*   **Mocks Permitidos?** SIM.

### 2. Testes de Integração (O Gargalo da Verdade)
*   **O que testar:** Queries SQL, Chamadas de API, Leitura de Arquivos.
*   **Ferramenta:** `pytest` com fixtures reais (Docker containers).
*   **Mocks Permitidos?** **NÃO.** (Proibido estritamente para código gerado por IA).
    *   *Por que?* A IA tende a "alucinar" APIs que não existem. Se você mockar a API que a IA inventou, o teste passa, mas o código quebra em produção.
    *   *Solução:* O teste deve bater no banco real (container de teste) para garantir que a coluna, tabela e tipo de dado existem.

### 3. Testes de Contrato (Spec Check)
*   **O que testar:** Se a saída do código corresponde ao JSON Schema / Pydantic Model definido na Spec.
*   **Ferramenta:** `pydantic` (Runtime validation).

---

## Workflow de TDD com IA (AI-TDD)

1.  **Humano:** Escreve o teste de integração (que falha inicialmente).
    *   Exemplo: `test_create_user_real_db.py`
2.  **IA:** Gera a implementação para fazer o teste passar.
3.  **Sistema:** Roda o teste.
4.  **Loop:** Se falhar, a IA recebe o output do erro e tenta novamente.

## Checklist de Aprovação de PR (Gerado por IA)

- [ ] O código possui Type Hints em todas as funções?
- [ ] Existe pelo menos 1 teste de integração que conecta no DB/API real?
- [ ] O script `pre_flight.py` passou com sucesso?
- [ ] Nenhuma credencial foi hardcoded (uso de env vars)?
