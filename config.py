from pydantic_settings import BaseSettings, SettingsConfigDict

class AzureConfig(BaseSettings):
    endpoint: str
    api_key: str
    api_version: str
    deployment: str
    model: str = "gpt-4.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AZURE_OPENAI_"
    )

azure_config = AzureConfig()
