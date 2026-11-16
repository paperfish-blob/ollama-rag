"""Single place for every tunable setting.

Precedence (lowest -> highest):  defaults below  <  environment variable  <  CLI flag.
Later stages add their own settings here (chunk size, top-k, ...), so you
never have to hunt through the code to find a magic number.
"""

import os
from dataclasses import dataclass, replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    # --- Ollama ---
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    chat_model: str = os.getenv("RAG_CHAT_MODEL", "llama3.2:3b")

    # --- Chat behaviour (Stage 1) ---
    system_prompt: str = os.getenv(
        "RAG_SYSTEM_PROMPT",
        "You are a helpful assistant. Keep answers concise.",
    )
    # Context window (in tokens) we ask Ollama to allocate. Why we set it
    # explicitly: if the conversation exceeds this, Ollama silently drops the
    # OLDEST tokens instead of raising an error, so the model "forgets" early
    # turns. Making it visible and configurable lets you observe that.
    num_ctx: int = int(os.getenv("RAG_NUM_CTX", "4096"))
    temperature: float = float(os.getenv("RAG_TEMPERATURE", "0.7"))

    # --- Paths (used from Stage 2 on) ---
    docs_dir: Path = PROJECT_ROOT / "docs"
    data_dir: Path = PROJECT_ROOT / "data"


def load_config(**cli_overrides) -> Config:
    """Defaults/env first, then apply any CLI flags that were actually given.

    CLI flags that the user did not pass arrive as None and are ignored, so
    they never clobber an env var or default.
    """
    given = {k: v for k, v in cli_overrides.items() if v is not None}
    return replace(Config(), **given)
