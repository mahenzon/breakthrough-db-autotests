from pydantic import BaseModel
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class PostgresConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr = SecretStr("password")
    admin_db: str = "postgres"
    testing_db: str = "test_sql_course"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TEST_CONFIG__",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pg: PostgresConfig = PostgresConfig()


settings = Settings()
