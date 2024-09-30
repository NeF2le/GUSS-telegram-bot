from pydantic_settings import BaseSettings
from pydantic import SecretStr
import os


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
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
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def google_creds_path(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.GOOGLE_CREDS_PATH)

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')


settings = Settings()
