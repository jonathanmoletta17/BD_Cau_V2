📁 03_MAPA_DE_INTENÇÕES.md
# 03 — Mapa de Intenções (DMD v2.1)

O agente deve reconhecer **apenas as intenções oficiais**. Qualquer outra entrada é UNKNOWN.

## Intenções Oficiais

1. **RESET_PASSWORD**  
   Problema de acesso/login.  
   Escopo: Rede, AD, E-mail integrado.

2. **CREATE_USER**  
   Solicitação de nova identidade digital.

3. **EQUIPMENT_REQUEST**  
   Pedido ou problema de equipamento físico.

4. **PRINTER_ISSUE**  
   Problemas com impressoras departamentais.

5. **VPN_ACCESS**  
   Concessão de acesso remoto (VPN).

6. **CORPORATE_SYSTEMS**  
   Erros em sistemas corporativos (ERP/CRM/etc.).

---

## Notas Importantes

- **HARDWARE_ISSUE** foi extinto e absorvido por **EQUIPMENT_REQUEST**.
- O agente nunca deve mencionar hardware pessoal como coberto.
- A classificação deve seguir a prioridade e regras estritas definidas no DMD.

---
