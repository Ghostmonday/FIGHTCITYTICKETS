import warnings
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "dev"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/fightsf"

    # Stripe Configuration
    stripe_secret_key: str = "change-me"
    stripe_publishable_key: str = "change-me"
    stripe_webhook_secret: str = "change-me"

    # Stripe Price IDs (test mode)
    stripe_price_standard: str = "price_1SedsMLncfs9uXKNp1q7FWc7"  # $9.89 test
    stripe_price_certified: str = "price_1SedsaLncfs9uXKN7YnRzjt4"  # $19.89 test

    # Lob Configuration
    lob_api_key: str = "change-me"
    lob_mode: str = "test"  # "test" or "live"

    # AI Services - DeepSeek
    deepseek_api_key: str = "change-me"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # AI Services - OpenAI
    openai_api_key: str = "change-me"

    # Application URLs
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"

    # Security
    secret_key: str = "dev-secret-change-in-production"

    @property
    def debug(self) -> bool:
        return self.app_env == "dev"

    def cors_origin_list(self) -> List[str]:
        # supports comma-separated origins
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator(
        "secret_key",
        "stripe_secret_key",
        "stripe_webhook_secret",
        "lob_api_key",
        "deepseek_api_key",
        "openai_api_key",
        mode="after",
    )
    @classmethod
    def validate_secrets_not_default(cls, v: str, info) -> str:
        """Validate that secrets are not using default/placeholder values."""
        field_name = info.field_name
        default_values = {
            "secret_key": "dev-secret-change-in-production",
            "stripe_secret_key": "change-me",
            "stripe_webhook_secret": "change-me",
            "lob_api_key": "change-me",
            "deepseek_api_key": "change-me",
            "openai_api_key": "change-me",
        }

        if field_name in default_values and v == default_values[field_name]:
            # Get environment from context if available
            import os

            app_env = os.getenv("APP_ENV", "dev")

            if app_env == "prod":
                raise ValueError(
                    f"{field_name} must be changed from default value in production environment"
                )
            elif app_env in ["staging", "test"]:
                warnings.warn(
                    f"Warning: {field_name} is using default value in {app_env} environment. "
                    f"This should be changed before production deployment.",
                    UserWarning,
                )
            else:
                # dev environment - just log warning
                print(
                    f"⚠️  Warning: {field_name} is using default value. Change this before production."
                )

        return v

    @field_validator("stripe_secret_key", mode="after")
    @classmethod
    def validate_stripe_key_format(cls, v: str) -> str:
        """Validate Stripe secret key format."""
        if v == "change-me":
            return v

        if not v.startswith(("sk_test_", "sk_live_")):
            warnings.warn(
                f"Stripe secret key doesn't match expected format. "
                f"Expected 'sk_test_...' or 'sk_live_...', got '{v[:10]}...'",
                UserWarning,
            )
        return v

    @field_validator("stripe_publishable_key", mode="after")
    @classmethod
    def validate_stripe_publishable_key_format(cls, v: str) -> str:
        """Validate Stripe publishable key format."""
        if v == "change-me":
            return v

        if not v.startswith(("pk_test_", "pk_live_")):
            warnings.warn(
                f"Stripe publishable key doesn't match expected format. "
                f"Expected 'pk_test_...' or 'pk_live_...', got '{v[:10]}...'",
                UserWarning,
            )
        return v

    @field_validator("stripe_webhook_secret", mode="after")
    @classmethod
    def validate_stripe_webhook_secret_format(cls, v: str) -> str:
        """Validate Stripe webhook secret format."""
        if v == "change-me":
            return v

        if not v.startswith("whsec_"):
            warnings.warn(
                f"Stripe webhook secret doesn't match expected format. "
                f"Expected 'whsec_...', got '{v[:10]}...'",
                UserWarning,
            )
        return v

    @field_validator("lob_api_key", mode="after")
    @classmethod
    def validate_lob_key_format(cls, v: str) -> str:
        """Validate Lob API key format."""
        if v == "change-me":
            return v

        if not v.startswith(("test_", "live_")):
            warnings.warn(
                f"Lob API key doesn't match expected format. "
                f"Expected 'test_...' or 'live_...', got '{v[:10]}...'",
                UserWarning,
            )
        return v

    def validate_production_settings(self) -> bool:
        """Validate all settings for production environment."""
        import os

        if self.app_env != "prod":
            return True

        errors = []
        warnings_list = []

        # Check for default secrets
        default_checks = [
            ("secret_key", "dev-secret-change-in-production"),
            ("stripe_secret_key", "change-me"),
            ("stripe_webhook_secret", "change-me"),
            ("lob_api_key", "change-me"),
            ("deepseek_api_key", "change-me"),
            ("openai_api_key", "change-me"),
        ]

        for field_name, default_value in default_checks:
            current_value = getattr(self, field_name)
            if current_value == default_value:
                errors.append(f"{field_name} is using default value '{default_value}'")

        # Check Stripe mode
        if self.stripe_secret_key.startswith("sk_test_"):
            warnings_list.append("Stripe is in test mode (sk_test_)")

        # Check Lob mode
        if self.lob_mode == "test":
            warnings_list.append("Lob is in test mode")

        # Check database URL
        if "postgres:postgres@" in self.database_url:
            warnings_list.append(
                "Database is using default credentials 'postgres:postgres'"
            )

        if errors:
            error_msg = "Production configuration errors:\n" + "\n".join(
                f"  • {e}" for e in errors
            )
            raise ValueError(error_msg)

        if warnings_list:
            warning_msg = "Production configuration warnings:\n" + "\n".join(
                f"  ⚠️  {w}" for w in warnings_list
            )
            print(warning_msg)

        return True


settings = Settings()
