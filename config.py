from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Общее
    app_env: str = "development"
    log_level: str = "INFO"

    # VK — получение
    vk_token: str = ""
    vk_owner_id: str = "publicnsmk"
    vk_api_version: str = "5.199"
    vk_days_back: int = 7

    # VK — публикация
    vk_community_token: str = ""
    vk_group_id: int = -176725270

    # GigaChat
    giga_credentials: str = ""
    giga_model: str = "GigaChat-2"
    giga_base_url: str = "https://api.giga.chat/v1"
    giga_verify_ssl: bool = False

    # Файлы
    prompt_template_file: str = "files/prompt_template.txt"
    prompt_file: str = "files/gigachat_prompt.txt"
    result_file: str = "files/gigachat_result.txt"

    # Поведение
    publish_require_confirm: bool = True

    def path(self, name: str) -> Path:
        """Путь к файлу в корне проекта (а не в текущей рабочей директории)."""
        return BASE_DIR / name


settings = Settings()