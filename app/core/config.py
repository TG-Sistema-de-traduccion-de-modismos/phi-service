from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8005
    host: str = "0.0.0.0"
    phi_model_url: str = "https://pablo-escobar.tailb1f41b.ts.net/phi-model"  
    
    class Config:
        env_file = ".env"

settings = Settings()