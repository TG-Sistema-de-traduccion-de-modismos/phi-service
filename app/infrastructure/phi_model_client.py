import httpx
from app.core.config import settings
from app.core.logging_config import logger

class PhiModelClient:
    def __init__(self):
        self.base_url = settings.phi_model_url.rstrip("/")
        self.timeout = 90.0

    async def corregir_gramatica(self, frase: str) -> str:
        url = f"{self.base_url}/correct"
        payload = {"frase": frase}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("frase_corregida", frase)
        except Exception as e:
            logger.error(f"Error al contactar phi-model: {e}")
            raise

    async def health_check(self) -> dict:
        url = f"{self.base_url}/health"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error al verificar salud de phi-model: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}