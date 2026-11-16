# ollama-rag

A local RAG assistant, built in stages to learn how RAG works end to end.
Everything runs locally via Ollama. No cloud APIs.

## Setup

```bash
uv sync                      # installs Python 3.12 + deps
ollama pull llama3.2:3b      # already pulled
ollama pull llama3.1:8b      # already pulled
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
