from pydantic import BaseModel
from typing import Optional

# Este es el modelo de datos que ESPERAMOS recibir
# en nuestro endpoint. FastAPI lo usará para validar.
class ReportRequest(BaseModel):
    prompt: str
    tenant_schema: Optional[str] = None  # Schema del tenant para multi-tenancy