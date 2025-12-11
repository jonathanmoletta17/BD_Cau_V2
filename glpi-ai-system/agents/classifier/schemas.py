from pydantic import BaseModel, Field
from typing import Optional, List

class ClassificationInput(BaseModel):
    summary: str = Field(..., description="Título ou resumo do problema")
    description: str = Field(..., description="Descrição detalhada do problema")

class ClassificationResult(BaseModel):
    category_id: str = Field(..., description="ID da categoria selecionada")
    category_name: str = Field(..., description="Nome hierárquico completo da categoria")
    confidence: float = Field(..., description="Nível de confiança da classificação (0.0 a 1.0)")
    reasoning: str = Field(..., description="Explicação curta do motivo da escolha")
    alternatives: Optional[List[str]] = Field(default=[], description="Outras categorias consideradas (top 2 e 3)")
