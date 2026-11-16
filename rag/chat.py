"""Stage 1 - a streaming terminal chat with memory.

The key idea: the model has NO memory. Every turn we resend the entire
conversation so far as a list of messages. "Memory" == this list.
"""

import httpx  # installed as a dependency of the ollama library
import ollama

from rag.config import Config

HELP = "Commands: /reset  clear history | /history  show the raw message list | /exit  quit"


def new_history(cfg: Config) -> list[dict]:
    # The system message goes first and sets the assistant's behaviour.
    # It is part of the list, so it is resent (and paid for in tokens) every turn.
    return [{"role": "system", "content": cfg.system_prompt}]


def stream_reply(client: ollama.Client, cfg: Config, history: list[dict]) -> tuple[str, dict]:
    """Send the full history, print tokens as they arrive, return (text, stats)."""
    stream = client.chat(
        model=cfg.chat_model,
        messages=history,
        stream=True,
        options={"num_ctx": cfg.num_ctx, "temperature": cfg.temperature},
    )
    parts: list[str] = []
    stats: dict = {}
    for chunk in stream:
        piece = chunk.message.content or ""
        print(piece, end="", flush=True)  # flush so tokens appear immediately
        parts.append(piece)
        # Only the final chunk (done=True) carries the token counts.
        if chunk.done:
            stats = {
                "prompt_tokens": chunk.prompt_eval_count,  # everything we SENT
                "reply_tokens": chunk.eval_count,          # what the model WROTE
            }
    print()
    return "".join(parts), stats


def run_chat(cfg: Config) -> None:
    client = ollama.Client(host=cfg.ollama_host)
    history = new_history(cfg)

    print(f"Model: {cfg.chat_model}  |  context window: {cfg.num_ctx} tokens")
    print(HELP + "\n")

    while True:
        try:
            user_input = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):  # Ctrl-D / Ctrl-C
            print()
            break
        if not user_input:
            continue

        if user_input == "/exit":
            break
        if user_input == "/reset":
            history = new_history(cfg)
            print("[history cleared]\n")
            continue
        if user_input == "/history":
            for i, m in enumerate(history):
                print(f"  [{i}] {m['role']:<9} {m['content'][:70]!r}")
            print()
            continue

        history.append({"role": "user", "content": user_input})
        try:
            print("bot > ", end="", flush=True)
            reply, stats = stream_reply(client, cfg, history)
        except ollama.ResponseError as e:  # e.g. model not pulled
            history.pop()  # don't keep a user turn that never got an answer
            print(f"\n[ollama error: {e.error}]\n")
            continue
        # httpx.ConnectError is what the ollama library actually raises when the server
        # is down. It is NOT a subclass of the built-in ConnectionError, so catch both.
        except (ConnectionError, httpx.ConnectError):
            history.pop()
            print("\n[cannot reach Ollama - is it running? try: ollama serve]\n")
            continue

        history.append({"role": "assistant", "content": reply})

        used = stats.get("prompt_tokens", 0) + stats.get("reply_tokens", 0)
        warn = "  !! near/over the window: oldest turns may be dropped" if used > 0.9 * cfg.num_ctx else ""
        print(
            f"[sent {stats.get('prompt_tokens')} tokens, got {stats.get('reply_tokens')}"
            f" | {len(history)} messages | {used}/{cfg.num_ctx} of window]{warn}\n"
        )
