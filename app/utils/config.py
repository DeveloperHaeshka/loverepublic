import json

from pydantic import BaseSettings, validator


class DB(BaseSettings):
    
    host: str
    port: int
    name: str
    user: str
    password: str


class Redis(BaseSettings):
    
    host: str
    db: int


class Bot(BaseSettings):
    
    token: str
    timezone: str
    admins: list[int]
    use_redis: bool

    @validator("admins", pre=True, always=True)
    def admin_ids(cls, string) -> list[int]:
        
        return json.loads(string)


class Webhook(BaseSettings):

    url: str
    port: int


class Payments(BaseSettings):

    project_id: int
    project_secret: str


class Settings(BaseSettings):
    
    bot: Bot
    db: DB
    redis: Redis
    webhook: Webhook
    payments: Payments

    class Config:
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(env_file=".env") -> Settings:
    """
    Loads .env file into BaseSettings

    :param str env_file: Env file, defaults to ".env"
    :return Settings: Settings object
    """
    
    settings = Settings(_env_file=env_file)
    return settings
