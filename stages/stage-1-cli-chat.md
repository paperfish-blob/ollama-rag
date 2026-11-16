# Stage 1: CLI chat

> Status: done · Date: 2026-11-16 · Models used: llama3.2:3b, llama3.1:8b

## Concept
A chat model is **stateless**: it remembers nothing between calls. A conversation only
feels continuous because our program resends the whole history as a list of messages
on every turn.

```
turn 1 sends: [system, user1]                                        -> reply1
turn 2 sends: [system, user1, assistant1, user2]                     -> reply2
turn 3 sends: [system, user1, assistant1, user2, assistant2, user3]  -> reply3
              └──────────────── grows every turn ────────────────┘
```

Two consequences:
- **Cost and latency grow.** More tokens are sent each turn, and the system prompt is
  paid for every time.
- **The context window is a hard ceiling** (`num_ctx` tokens). When the history is bigger,
  Ollama silently drops the oldest tokens. There is no error; the model just "forgets".

This is why RAG exists: you cannot paste all your notes into every prompt, so you
retrieve only the relevant pieces.

## What was built
| File | Purpose |
|---|---|
| [rag/config.py](../rag/config.py) | All settings. Precedence: defaults < env vars < CLI flags |
| [rag/chat.py](../rag/chat.py) | Streaming chat loop, history list, `/reset` `/history` `/exit`, token stats |
| [main.py](../main.py) | CLI entry point, `chat` subcommand |

## Run it
```bash
uv run main.py chat
uv run main.py chat --model llama3.1:8b
```
**Expected output:** streamed tokens, then a stats line after every reply:
```
[sent 46 tokens, got 33 | 3 messages | 79/256 of window]
```
`sent` = tokens in the whole history we resent. `got` = tokens the model wrote.

## What you just learned
- The chat model is stateless. A conversation is a `list[dict]` of `role`/`content` messages your code resends.
- Tokens sent grow every turn, and the system prompt is paid for each time.
- The context window is a hard ceiling. Overflow means silent forgetting of the oldest content, not an error.
- Streaming is iterating over chunks. Only the final chunk carries token counts (`prompt_eval_count`, `eval_count`).
- Models state wrong answers with full confidence, which is the case for grounding them in your own data.

## Exercises

### Exercise 1: Force the context overflow
**Goal:** see that the model forgets early turns when the history exceeds the window.
**Command:**
```bash
uv run main.py chat --num-ctx 256 --temperature 0
```
**Type these:**
```
My name is Alex and my favourite planet is Saturn.
Explain in about 100 words what photosynthesis is.
Explain in about 100 words how a volcano erupts.
Explain in about 100 words how a bicycle gear works.
What is my name and my favourite planet?
```
**Watch for:**
- The `messages` count rises every turn, but `sent` stops rising and then falls.
- The `!!` warning once usage passes 90% of the window.
- The last answer: does the bot still know your name?

**Example run** (llama3.2:3b, temp 0):

| Turn | Messages | Tokens sent | Note |
|---|---|---|---|
| 1 | 3 | 46 | fits |
| 2 | 5 | 100 | fits |
| 3 | 7 | 228 | near the 256 limit |
| 4 | 9 | **205** | history grew, tokens sent fell |
| 5 | 11 | **187** | bot: "I don't have that information..." |

Control run with `--num-ctx 4096`: 507 tokens sent, answer: "Your name is Alex, and your favourite planet is Saturn."
**Why it happens:** your program still holds all 11 messages (check with `/history`), but Ollama only reads the newest tokens that fit. Turn 1, containing your name, was cut off.
**Your turn:** find the smallest `--num-ctx` at which the bot still remembers your name after the same five lines.

### Exercise 2: Compare the 3B and 8B models
**Goal:** see that a bigger model is better but still not reliable.
**Command** (run once per model):
```bash
uv run main.py chat --model llama3.2:3b --temperature 0
uv run main.py chat --model llama3.1:8b --temperature 0
```
**Type these:**
```
What is the capital of Australia?
A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Answer with the number only.
How many days are there from 3 March to 19 June in the same non-leap year? Answer with the number only.
What is 4871 x 3296? Answer with the number only.
```
**Watch for:**
- Which questions each model gets right (correct answers: Canberra, 0.05, 108, 16054816).
- Whether a wrong answer sounds less confident than a right one (it does not).
- The wait before the first token. The 8B is usually slower; judge it yourself (I did not time it).

**Example run** (temp 0):

| Question | Correct | llama3.2:3b | llama3.1:8b |
|---|---|---|---|
| Capital of Australia | Canberra | Canberra | Canberra |
| Bat and ball | 0.05 | 0.05 | 0.05 |
| Days 3 Mar to 19 Jun | 108 | 153 | 116 |
| 4871 x 3296 | 16054816 | 160,111,016 | 16044496 |

**Why it happens:** models predict plausible text; they do not calculate. The larger model is closer (116, 16044496) but still wrong. Facts a model has seen often are reliable; exact arithmetic is not. This is the motivation for Stage 5 (tools).
**Your turn:** ask each model a fact about something obscure you can verify (a small town's population, a minor historical date) and see who guesses.

### Exercise 3: Change the personality with the system prompt
**Goal:** see how one hidden message steers all behaviour.
**Command** (run once per system prompt):
```bash
uv run main.py chat --temperature 0 --system "You are a pirate. Answer in one sentence."
uv run main.py chat --temperature 0 --system "You are a patient teacher. Explain like I am 12, with an analogy."
```
**Type these:**
```
Why is the sky blue?
What is photosynthesis?
```
**Watch for:**
- The same questions get completely different styles.
- Whether the model obeys the constraint ("one sentence").

**Example run** (llama3.2:3b, temp 0):
- Pirate: "Arrr, matey, the sky be blue because o' the way the sunlight scatters off the tiny particles in the atmosphere..." (kept the pirate voice, but the photosynthesis answer ran past one sentence)
- Teacher: "So, you know how we can see lots of different colors... It's like a big ol' rainbow in the sky..."

**Why it happens:** the system message is the first item in the list the model reads on every turn. It steers tone and format, but a 3B model follows rules like "one sentence" only loosely. In Stage 3 this same slot will carry "answer only from the context below", so expect the same looseness.
**Your turn:** write a system prompt that forces answers to be exactly one word, and test how often the 3B model breaks it.

## Changes to earlier stages
None (first stage).

## Limits and gotchas
- `num_ctx` overflow is silent. The stats line is our only warning, and it is an estimate based on the last turn.
- History is kept in memory only. Closing the program loses it.
- Larger `num_ctx` uses more RAM and slows the first token.
- Output varies between runs unless `--temperature 0` is set; even then it may differ across Ollama versions.

## Next
Stage 2: Ingest (sample notes, chunking, embeddings, numpy store, then ChromaDB). Say "next" to start.
