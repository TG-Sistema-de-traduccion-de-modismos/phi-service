from fastapi import APIRouter, HTTPException
from app.domain.models import FraseEntrada, FraseSalida, CambioDetalle
from app.application.neutralizer import PhiNeutralizer
from app.infrastructure.phi_model_client import PhiModelClient

router = APIRouter()
neutralizer = PhiNeutralizer()
model_client = PhiModelClient()


@router.get("/health")
async def health_check():
    model_health = await model_client.health_check()
    return {
        "status": "healthy",
        "model_service": model_health
    }


@router.post("/neutralizer", response_model=FraseSalida)
async def neutralizar(data: FraseEntrada):
    try:
        # Obtener la frase neutralizada y los cambios con posiciones
        frase_neutralizada, cambios = await neutralizer.neutralizar(
            data.frase, 
            data.significado
        )
        
        # Convertir a objetos CambioDetalle
        cambios_detalle = [
            CambioDetalle(**cambio) for cambio in cambios
        ]
        
        return FraseSalida(
            original=data.frase,
            neutralizada=frase_neutralizada,
            cambios=cambios_detalle
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))