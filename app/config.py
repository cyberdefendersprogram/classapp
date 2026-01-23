from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "Class Portal"
    version: str = "1.0.0"
    env: str = "development"
    log_level: str = "INFO"

    # Security
    secret_key: str = "change-me-in-production"
    base_url: str = "http://localhost:8000"

    # Google Sheets
    google_sheets_id: str = ""
    google_service_account_path: str = "/etc/classapp/service-account.json"

    # Forward Email API
    forwardemail_api_url: str = "https://api.forwardemail.net/v1/emails"
    forwardemail_user: str = ""
    forwardemail_pass: str = ""

    # Magic link settings
    magic_link_ttl_minutes: int = 15
    rate_limit_per_email_15m: int = 3

    # SQLite
    sqlite_path: str = "data/app.db"

    @property
    def is_development(self) -> bool:
        return self.env == "development"


settings = Settings()
