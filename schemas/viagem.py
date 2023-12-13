from pydantic import BaseModel, Field
from flask_openapi3 import FileStorage
from typing import Optional, List


class ViagemSchema(BaseModel):
    destino: str
    detalhes: str
    rating: float
    fotos: List[FileStorage]
  
class ViagemViewSchema(BaseModel):
    id: int
    destino: str
    detalhes: str
    rating: float
    fotos: str

class ViagemBuscaSchema(BaseModel):
    id: Optional[int]
    destino: Optional[str]

class ViagemUpdateSchema(BaseModel):
    id: int
    destino: Optional[str] = None
    detalhes: Optional[str] = None
    rating: Optional[int] = None
    fotos: List[FileStorage] = None

class ViagemDelSchema(BaseModel):
    id: int

def apresenta_viagem(viagem):
    return {
        "id": viagem.id,
        "destino": viagem.destino,
        "detalhes": viagem.detalhes,
        "rating": float(viagem.rating),
        "fotos": viagem.fotos,
    }

class ViagemListaViewSchema(BaseModel):
    viagem: List[ViagemViewSchema]

def apresenta_lista_viagem(viagem):
    result = []
    for viagem in viagem:
        result.append(apresenta_viagem(viagem))
    return {"viagem": result}