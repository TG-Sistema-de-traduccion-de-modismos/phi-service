from pydantic import BaseModel
from typing import Dict, List

class FraseEntrada(BaseModel):
    frase: str
    significado: Dict[str, str]

class CambioDetalle(BaseModel):
    palabra: str
    indice_inicio: int  
    indice_fin: int     
class FraseSalida(BaseModel):
    original: str
    neutralizada: str
    cambios: List[CambioDetalle]