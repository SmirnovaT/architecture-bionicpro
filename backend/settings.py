from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    allow_origins: list[str] = ["http://localhost:3000"]
    host: str = "0.0.0.0"
    port: int = 8000

    keycloak_url: str = "http://keycloak:8080"
    keycloak_realm: str = "reports-realm"
    keycloak_client_id: str = "reports-api"
    keycloak_client_secret: str = "oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq"
    required_role: str = "prosthetic_user"

    log_level: str = "INFO"


settings = Settings(_env_file=".env")
