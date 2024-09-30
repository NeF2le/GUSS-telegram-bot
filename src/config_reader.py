from pydantic_settings import BaseSettings
from pydantic import SecretStr
import os


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    BOT_TOKEN: SecretStr
    VK_TOKEN: SecretStr
    ADMIN_IDS: list[int]
    VK_GROUP_DOMAINS: list[str | int]
    PAGINATION_LOAD_LIMIT: int
    VK_GROUP_POSTS_COUNT: int
    VK_LIKE_POINTS: int
    VK_COMMENT_POINTS: int
    VK_ACTIVITIES_CHECKER_TIMEOUT: int
    ACTION_LOGS_LIMIT: int
    PERSON_MATCH_THRESHOLD: int
    COMMITTEE_ATTENDANCE_POINTS: int
    GOOGLE_CREDS_PATH: str

    @property
    def database_url_asyncpg(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def google_creds_path(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.GOOGLE_CREDS_PATH)

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')


settings = Settings()
