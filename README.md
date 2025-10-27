# **PHI Service**

**Servicio orquestador para neutralización de modismos.**
Este servicio actúa como intermediario entre el orquestador y phi-model, gestionando las peticiones de neutralización, validando entradas y procesando respuestas.

## **Resumen**
**PHI Service** se encarga de:
- **Recibir** peticiones del orquestador
- **Validar** el formato de entrada (frase y diccionario de significados)
- **Comunicarse** con phi-model
- **Procesar** las respuestas
- **Formatear** y entregar los resultados neutralizados

---

## **Tecnologías principales**
- FastAPI
- Pydantic para validación
- httpx para comunicación asíncrona
- Python 3.10+
- Docker

---

## **Estructura del proyecto**
```
phi-service/
├── Dockerfile
├── requirements.txt
├── .env
└── app/
    ├── main.py              # Punto de entrada FastAPI
    ├── infrastructure/
    │   └── routes.py                  # Endpoints HTTP
    │   └── phi_model_client.py        
     # Endpoints HTTP
    ├── application/
    │   └── neutralizer.py       # Lógica de comunicación con phi-model
    ├── core/
    │   ├── config.py        # Configuración
    │   └── logging_config.py
    └── domain/
        └── models.py        # Modelos Pydantic
```

---

## **Endpoints**

### **GET /health**
Verifica:
- Estado del servicio
- Conectividad con phi-model
- Configuración activa

### **POST /neutralize**
Endpoint principal que:
1. Recibe frase y diccionario de significados
2. Valida formato y longitud
3. Comunica con phi-model
4. Procesa respuesta
5. Retorna texto neutralizado

**Entrada:**
```json
{
    "frase": "Ese man está echando los perros a esa vieja",
    "significado": {
        "ese man": "esa persona",
        "echando los perros": "coqueteando",
        "esa vieja": "esa mujer"
    }
}
```

**Respuesta:**
```json
{
    "texto_original": "Ese man está echando los perros a esa vieja",
    "texto_neutralizado": "Esa persona está coqueteando con esa mujer",
    "tiempo_proceso": 0.234,
    "modelo_usado": "microsoft/Phi-3-mini-4k-instruct"
}
```

---

## **Docker — Build & Run**

1) Construir:
```sh
docker build -t phi-service:latest ./phi-service
```
> **Nota:** la imagen resultante pesa aproximadamente **1 GB**.

2) Ejecutar:
```sh
docker run --rm --name phi-service \
    -p 8005:8005 \
    --env-file .env \
    phi-service:latest
```

---

## **Configuración**
- Ajustar variables en `.env` y `config.py` según tu entorno:
  - URLs de servicios
  - Puertos
  - Timeouts
  - Niveles de logging

---

## **Integración y dependencias**
- Requiere acceso a **phi-model**
- Diseñado para trabajar con el orquestador principal
- Compatible con orquestación via docker-compose
- Se integra con **beto-service** en el pipeline completo

---

## **Notas operativas**
- Servicio stateless
- Optimizado para procesamiento asíncrono
- Incluye circuit breakers para fallos de phi-model
- Logging estructurado para monitoreo****
