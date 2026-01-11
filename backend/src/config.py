import warnings
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "dev"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/fights"

    # Stripe Configuration
    # IMPORTANT: Set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET in .env
    # Use sk_live_... for production, sk_test_... for testing
    stripe_secret_key: str = "sk_live_dummy"  # Override with STRIPE_SECRET_KEY env var
    stripe_publishable_key: str = (
        "pk_live_dummy"  # Override with STRIPE_PUBLISHABLE_KEY env var
    )
    stripe_webhook_secret: str = (
        "whsec_dummy"  # Override with STRIPE_WEBHOOK_SECRET env var
    )

    # Stripe Price IDs - Set these in .env for production
    # Get live price IDs from: https://dashboard.stripe.com/products
    stripe_price_standard: str = ""  # Set STRIPE_PRICE_STANDARD in .env
    stripe_price_certified: str = ""  # Set STRIPE_PRICE_CERTIFIED in .env

    # Lob Configuration
    lob_api_key: str = "test_dummy"
    lob_mode: str = "test"  # "test" or "live"

    # Hetzner Cloud Configuration
    hetzner_api_token: str = "change-me"  # Override with HETZNER_API_TOKEN env var
    hetzner_droplet_name: Optional[str] = (
        None  # Override with HETZNER_DROPLET_NAME env var
    )

    # AI Services - DeepSeek
    deepseek_api_key: str = "sk_dummy"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # AI Services - OpenAI
    openai_api_key: str = "sk_dummy"

    # Application URLs
    app_url: str = "http://localhost:3000"  # Override with APP_URL env var
    api_url: str = "http://localhost:8000"  # Override with API_URL env var

    # Security
    secret_key: str = "dev_secret_change_in_production"

    # Civil Shield Compliance Versioning
    clerical_engine_version: str = "2.1.0"
    compliance_version: str = "civil_shield_v1"

    # Service Fees (in cents)
    fightcity_service_fee: int = 1989  # $19.89 for certified
    fightcity_standard_fee: int = 989  # $9.89 for standard

    @property
    def debug(self) -> bool:
        return self.app_env == "dev"

    def cors_origin_list(self) -> list[str]:
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
            "hetzner_api_token": "change-me",
        }

        if field_name in default_values and v == default_values[field_name]:
            # Get environment from context if available
            import os

            app_env = os.getenv("APP_ENV", "dev")

            if app_env == "prod":
                raise ValueError(
                    "{field_name} must be changed from default value in production environment"
                )
            elif app_env in ["staging", "test"]:
                warnings.warn(
                    "Warning: {field_name} is using default value in {app_env} environment. "
                    "This should be changed before production deployment.",
                    UserWarning,
                    stacklevel=2,
                )
            else:
                # dev environment - just log warning
                print(
                    "⚠️  Warning: {field_name} is using default value. Change this before production."
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
                "Stripe secret key doesn't match expected format. "
                "Expected 'sk_test_...' or 'sk_live_...', got '{v[:10]}...'",
                UserWarning,
                stacklevel=2,
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
                "Stripe publishable key doesn't match expected format. "
                "Expected 'pk_test_...' or 'pk_live_...', got '{v[:10]}...'",
                UserWarning,
                stacklevel=2,
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
                "Stripe webhook secret doesn't match expected format. "
                "Expected 'whsec_...', got '{v[:10]}...'",
                UserWarning,
                stacklevel=2,
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
                "Lob API key doesn't match expected format. "
                "Expected 'test_...' or 'live_...', got '{v[:10]}...'",
                UserWarning,
                stacklevel=2,
            )
        return v

    def validate_production_settings(self) -> bool:
        """Validate all settings for production environment."""
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
                errors.append("{field_name} is using default value '{default_value}'")

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
                "  • {e}" for e in errors
            )
            raise ValueError(error_msg)

        if warnings_list:
            warning_msg = "Production configuration warnings:\n" + "\n".join(
                "  ⚠️  {w}" for w in warnings_list
            )
            print(warning_msg)

        return True


settings = Settings()
