from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "crypto"
    postgres_password: str
    postgres_db: str = "crypto"

    deribit_base_url: str = "https://www.deribit.com/api/v2"
    deribit_timeout: float = 10.0
    collect_interval: int = 60

    @property
    def database_url(self) -> str:
        return self._postgres_url("postgresql+asyncpg")

    @property
    def broker_url(self) -> str:
        return "sqla+" + self._postgres_url("postgresql+psycopg2")

    def _postgres_url(self, driver: str) -> str:
        url = URL.create(
            driver,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )
        return url.render_as_string(hide_password=False)
