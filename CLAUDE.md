# Project: ollama-rag — a local RAG assistant I'm building to LEARN

## Progress
- Stage 1 (CLI chat): DONE
- Next: Stage 2 (wait for the user to say "next")
- Decisions so far: models = `llama3.2:3b` (small), `llama3.1:8b` (large + tool calling), `nomic-embed-text` (embeddings, to pull at Stage 2). Machine: MacBook Pro M4 Pro, 24 GB. Python 3.12 via `uv`.
- Update this section at the end of every stage.
- Stage start and finish follow the project skill `stage-handoff` (`.claude/skills/stage-handoff/`). Each stage gets a note in `stages/` with generic (non-trading) default exercises and real captured output.
- Do not `git commit` or `git push` until I ask. Show me the changes first.

## Who I am and how to work with me
I'm a Product Owner with full-stack experience (Kotlin/Spring, TypeScript, some Python).
My goal is to **understand how RAG works end to end**, not just to have working code.

Working rules:
1. **Build in stages. Each stage must run on its own before we move on.**
   At the end of each stage, stop and give me:
   - the exact commands to run it
   - what output I should expect
   - a short "What you just learned" section (3–5 bullets)
   - 2–3 "Try this" experiments (e.g. change a parameter and observe the effect)
   Then **wait for me to say "next"** before starting the next stage.
2. Before writing code for a stage, explain the concept in plain language in a few
   short paragraphs, with a small diagram (ASCII is fine) where it helps.
3. Keep code simple and readable over clever. Comment the *why*, not the *what*.
4. Refactor earlier stages only when needed, and tell me what changed and why.
5. If something depends on my machine (RAM, GPU, model availability), ask me
   instead of guessing.

## Tech constraints
- Python 3.11+, managed with `uv` (or a venv + requirements.txt if simpler)
- Ollama running locally (http://localhost:11434), using the official `ollama` Python library
- Everything runs locally: no cloud APIs
- Config (model names, chunk size, overlap, top-k, paths) in one place
  (`config.py` or a `.env`), overridable by CLI flags
- Suggested models (check with me first): a small chat model (~3B), a larger one (~8B),
  a model that supports tool calling, and an embedding model such as `nomic-embed-text`

## Suggested structure (adjust if you have a good reason)
```
ollama-rag/
  docs/            # my markdown notes
  data/            # generated vector stores
  rag/
    config.py
    chat.py        # Stage 1
    ingest.py      # Stage 2
    retrieve.py    # Stage 3
    answer.py      # Stages 3–4
    tools.py       # Stage 5
  eval/            # Stage 6
  web/             # Stage 7
  main.py          # CLI entry point
  README.md        # update it at the end of every stage
```

---

## Stage 1 – CLI chat
- Streaming chat in the terminal with conversation history
- Configurable model name (config + `--model` flag)
- Commands: `/reset` to clear history, `/exit` to quit
- Explain: how chat history is just a list of messages resent each turn, and why
  that grows the context window

## Stage 2 – Ingest
- Load all `.md` files from `docs/`. I'll add my own trading notes later; to start,
  **create 5–6 realistic sample trading notes** (e.g. trade journal entries, a
  setup/strategy note, a risk-management rules note, a weekly market review, a
  post-mortem on a losing trade). Give each note a date in its front matter or
  filename so Stage 5 can filter by date.
- Chunk them. **Explain chunk size and overlap trade-offs** (too small = lost context,
  too large = diluted similarity and wasted tokens; overlap = continuity vs duplication).
  Store metadata per chunk: file, date, chunk index, text.
- Embed each chunk with an Ollama embedding model.
- **Version A:** store vectors in plain numpy + a JSON/pickle file, and do
  cosine similarity by hand, so I can see exactly how it works.
- **Version B:** switch to ChromaDB. Explain what it gives me over Version A
  (persistence, indexing, metadata filtering) and what it hides from me.
- Re-running ingest should not create duplicates.

## Stage 3 – Retrieve and answer
- Embed the question → find top-k chunks → build the prompt → answer **only from the
  retrieved context**
- Show me the final prompt template and explain each part
- It must say **"I don't know"** (or similar) when the answer isn't in my notes.
  Explain the techniques used (prompt instructions, a similarity score threshold, or both)
  and their limits.
- `--debug` flag: print the retrieved chunks with their similarity scores and source files
  before the answer

## Stage 4 – Citations
- Return answers as structured JSON:
  `{ "answer": str, "sources": [{ "file": str, "snippet": str }] }`
- Use Ollama's structured output / JSON schema support, and validate the result
  (e.g. with Pydantic). Handle invalid JSON gracefully.
- Render it nicely in the terminal (e.g. with `rich`): answer first, then numbered sources
- Explain how to stop the model from citing sources it wasn't given

## Stage 5 – Tool calling
- Give the model tools: `search_notes(query)` and `list_notes_by_date(from, to)`,
  and let it decide when to call them (loop until it returns a final answer; cap the
  number of tool calls)
- Print tool calls and their results in `--debug` mode
- **Explain how this differs from always retrieving before answering** (Stage 3):
  when each approach is better, cost/latency, failure modes (e.g. small models
  skipping or misusing tools)

## Stage 6 – Evaluate and compare
- Write **10 test questions with expected answers** based on the sample notes
  (include at least 2 questions whose answer is NOT in the notes, to test "I don't know")
- Run them against 2–3 models (e.g. a 3B and an 8B) and 2–3 chunk sizes
- Scoring: explain the options (exact match, keyword match, LLM-as-judge) and pick
  a simple one; tell me its weaknesses
- Print a comparison table: model × chunk size → accuracy, avg latency, avg retrieval score
- Save the results to a CSV, and give me a short interpretation of what the numbers say

## Stage 7 (optional) – Web UI
- A simple web chat UI on top of the **same core code** (no logic duplicated):
  either FastAPI + a minimal HTML page, or Streamlit. Recommend one and say why.
- Show the answer, the cited sources, and a toggle for debug info

---

## Finally
After Stage 6 (or 7), give me:
- a one-page summary of the full RAG pipeline in my own project's terms
- the 5 most important things to improve if this were going to production
  (e.g. hybrid search, re-ranking, better chunking, eval sets, observability)
