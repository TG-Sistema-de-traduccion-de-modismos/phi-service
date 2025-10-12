from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8005
    host: str = "0.0.0.0"
    phi_model_url: str = "http://phi-model:8006"
    
    class Config:
        env_file = ".env"

settings = Settings()