"""CLI entry point. Each stage adds a subcommand; for now there is only `chat`.

    uv run main.py chat
    uv run main.py chat --model llama3.1:8b
"""

import argparse

from rag.chat import run_chat
from rag.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ollama-rag")
    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat", help="Stage 1: streaming chat with history")
    chat.add_argument("--model", dest="chat_model", help="Ollama model name")
    chat.add_argument("--num-ctx", dest="num_ctx", type=int, help="context window in tokens")
    chat.add_argument("--temperature", type=float)
    chat.add_argument("--system", dest="system_prompt", help="system prompt text")
    return parser


def main() -> None:
    args = vars(build_parser().parse_args())
    command = args.pop("command")
    cfg = load_config(**args)  # remaining keys map 1:1 onto Config fields
    if command == "chat":
        run_chat(cfg)


if __name__ == "__main__":
    main()
