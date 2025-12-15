
import os
from datetime import datetime

def create_spec_template(feature_name):
    filename = f"docs/specs/{datetime.now().strftime('%Y%m%d')}_{feature_name}.md"
    
    template = f"""# Spec: {feature_name.replace('_', ' ').title()}

**Status:** Draft  
**Data:** {datetime.now().strftime('%d/%m/%Y')}

## 1. Objetivo de Negócio
<!-- O que essa funcionalidade resolve? -->

## 2. Contrato de Interface (Input/Output)
<!-- Defina JSONs, assinaturas de função e tipos de dados EXATOS -->

### Input
```json
{{
  "key": "type"
}}
```

### Output
```json
{{
  "result": "success"
}}
```

## 3. Regras de Negócio (Constraints)
1. <!-- Regra 1 -->
2. <!-- Regra 2 -->

## 4. Plano de Testes (Integration First)
- [ ] Teste de Caminho Feliz (Happy Path) com DB Real
- [ ] Teste de Erro (Edge Case)
"""
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"[OK] Spec Template criado em: {filename}")
    print("[NEXT] AGORA: Preencha o arquivo antes de pedir código para a IA.")
