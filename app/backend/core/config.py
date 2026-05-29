import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")

    VLM_PROVIDER: str = os.getenv("VLM_PROVIDER", "openai")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))

    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "mlruns")


settings = Settings()