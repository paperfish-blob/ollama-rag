# ollama-rag

A local RAG assistant, built in stages to learn how RAG works end to end.
Everything runs locally via Ollama. No cloud APIs.

## Prerequisites

| Requirement | Why | Check / install |
|---|---|---|
| macOS, Linux or Windows | Developed on macOS (Apple Silicon) | |
| RAM: 8 GB minimum, 16 GB+ recommended | The 3B model needs about 2-3 GB, the 8B about 5-6 GB, plus the OS and context window | Developed on 24 GB |
| [Ollama](https://ollama.com/download) running locally | Serves the chat and embedding models at `http://localhost:11434` | `ollama --version`, then `curl http://localhost:11434/api/version` |
| [uv](https://docs.astral.sh/uv/) | Manages Python and dependencies | `uv --version`, install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Python 3.11+ (3.12 used) | The language | `uv` downloads it for you, so a system Python is not required |
| Git | Clone and version the project | `git --version` |
| Disk: about 8 GB free | Model files (see below) | |

A GPU is not required. On Apple Silicon, Ollama uses the GPU automatically. On other machines it falls back to CPU, which is slower.

### Ollama models

| Model | Size | Used for | Stage |
|---|---|---|---|
| `llama3.2:3b` | 2.0 GB | Small, fast chat model | 1 onward |
| `llama3.1:8b` | 4.9 GB | Larger chat model, supports tool calling | 1 onward, 5 |
| `nomic-embed-text` | about 270 MB | Turns text into vectors | 2 onward |

```bash
ollama pull llama3.2:3b
ollama pull llama3.1:8b
ollama pull nomic-embed-text   # needed from Stage 2
ollama list                    # confirm they are installed
```

## Setup

```bash
git clone https://github.com/paperfish-blob/ollama-rag.git
cd ollama-rag
uv sync                      # installs Python 3.12 + dependencies into .venv
```

## Stage 1 - CLI chat  (done)

```bash
uv run main.py chat
uv run main.py chat --model llama3.1:8b --num-ctx 8192
```

Commands inside the chat: `/reset`, `/history`, `/exit`.

Config lives in [rag/config.py](rag/config.py) (defaults < env vars like `RAG_CHAT_MODEL` < CLI flags).

**Key idea:** the model is stateless. "Memory" is a list of messages that we resend in full on every
turn, so tokens sent per turn grow, and the context window (`num_ctx`) is the ceiling.

## Stages to come
2 Ingest · 3 Retrieve & answer · 4 Citations · 5 Tool calling · 6 Evaluate · 7 Web UI
