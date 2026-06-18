from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    try_to_occupy: bool
    session_file_path: str
    api_id: int
    api_hash: str


@lru_cache
def load_config() -> Config:
    return Config()
