from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    token_api: str
    payments_provider_token: str

    class Config:
        env_file = ".env"


settings = Settings()
