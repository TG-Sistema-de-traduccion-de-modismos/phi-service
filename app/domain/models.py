from pydantic import BaseModel
from typing import Dict

class FraseEntrada(BaseModel):
    frase: str
    significado: Dict[str, str]

class FraseSalida(BaseModel):
    original: str
    neutralizada: str