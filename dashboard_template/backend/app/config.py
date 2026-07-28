"""Dashboard application configuration via environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend directory (one level above app/)
_BACKEND_DIR = Path(__file__).resolve().parents[1]

# Always load backend/.env (active config)
_env_name = os.getenv("DASHBOARD_ENV_FILE", ".env")
_ENV_FILE = _BACKEND_DIR / _env_name


@dataclass(frozen=True)
class EnvironmentCredentials:
    """Supabase + Vercel project credentials for one environment."""

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    vercel_project_id: str
    vercel_project_name: str
    backend_api_url: str


class Settings(BaseSettings):
    """Dashboard settings loaded from backend/.env."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Data mode
    dashboard_data_mode: Literal["mock", "live"] = "mock"

    # Feature flags
    feature_supabase: bool = True
    feature_vercel: bool = False
    feature_host_health: bool = False
    feature_storage_metrics: bool = False
    feature_costs_module: bool = False
    feature_test_prod_switch: bool = True
    feature_datadog: bool = False
    feature_private_database: bool = False

    # Hosting provider
    hosting_provider: Literal["none", "render", "railway", "fly", "custom"] = "none"

    # Generic API URLs (renamed from Beeing-specific)
    main_api_url_test: str = ""
    main_api_url_prod: str = ""

    # Supabase — test
    supabase_url_test: str = ""
    supabase_anon_key_test: str = ""
    supabase_service_role_key_test: str = ""

    # Supabase — production
    supabase_url_prod: str = ""
    supabase_anon_key_prod: str = ""
    supabase_service_role_key_prod: str = ""

    # External providers (optional, shared across environments)
    openrouter_api_key: str = ""
    deepgram_api_key: str = ""

    # Vercel (team-specific, shared)
    vercel_base_url: str = "https://vercel.com"
    vercel_api_token: str = ""
    vercel_team_id: str = ""
    vercel_team_url: str = ""

    # Vercel (project-specific)
    vercel_project_id_test: str = ""
    vercel_project_name_test: str = ""
    vercel_project_id_prod: str = ""
    vercel_project_name_prod: str = ""

    # Hosting health URLs
    render_service_url: str = ""
    railway_service_url: str = ""
    fly_service_url: str = ""
    custom_service_url: str = ""

    # Dashboard auth
    api_key: str = Field(
        default="change-me-local-dev",
        validation_alias=AliasChoices("API_KEY"),
    )
    dashboard_allowed_emails: str = ""

    # Private database (non-Supabase)
    database_url: str = Field(default="", validation_alias=AliasChoices("DATABASE_URL"))
    database_url_read: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL_READ"),
    )

    # Datadog (optional extension)
    datadog_api_key: str = Field(default="", validation_alias=AliasChoices("DATADOG_API_KEY"))
    datadog_app_key: str = Field(default="", validation_alias=AliasChoices("DATADOG_APP_KEY"))
    datadog_site: str = Field(
        default="datadoghq.com",
        validation_alias=AliasChoices("DATADOG_SITE"),
    )

    # Server (PORT is injected by Render and other cloud hosts)
    dashboard_backend_host: str = "127.0.0.1"  # overridden to 0.0.0.0 when PORT is set
    dashboard_backend_port: int = Field(
        default=8001,
        validation_alias=AliasChoices("PORT", "DASHBOARD_BACKEND_PORT"),
    )
    dashboard_frontend_url: str = Field(
        default="http://localhost:5173",
        validation_alias=AliasChoices("FRONTEND_URL", "DASHBOARD_FRONTEND_URL"),
    )
    log_level: str = "INFO"

    # Costs module (generic pricing)
    costs_unit_price: float = 0.0
    costs_unit_name: str = ""
    costs_currency: str = "USD"

    def credentials_for(self, env: Literal["test", "prod"]) -> EnvironmentCredentials:
        if env == "prod":
            return EnvironmentCredentials(
                supabase_url=self.supabase_url_prod,
                supabase_anon_key=self.supabase_anon_key_prod,
                supabase_service_role_key=self.supabase_service_role_key_prod,
                vercel_project_id=self.vercel_project_id_prod,
                vercel_project_name=self.vercel_project_name_prod,
                backend_api_url=self.main_api_url_prod,
            )
        return EnvironmentCredentials(
            supabase_url=self.supabase_url_test,
            supabase_anon_key=self.supabase_anon_key_test,
            supabase_service_role_key=self.supabase_service_role_key_test,
            vercel_project_id=self.vercel_project_id_test,
            vercel_project_name=self.vercel_project_name_test,
            backend_api_url=self.main_api_url_test,
        )

    def backend_api_url_for(self, env: Literal["test", "prod"]) -> str:
        return self.credentials_for(env).backend_api_url

    def environment_available(self, env: Literal["test", "prod"]) -> bool:
        creds = self.credentials_for(env)
        return bool(creds.supabase_url and creds.supabase_service_role_key)


settings = Settings()
