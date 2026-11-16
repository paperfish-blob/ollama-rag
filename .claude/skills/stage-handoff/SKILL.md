---
name: stage-handoff
description: Standard procedure for starting and finishing each ollama-rag learning stage. Use at the start of every stage (concept explanation before code) and at the end (verified run, stage note, generic default exercises with real captured output, README and progress update). Use whenever the user says "next", asks to finish or wrap up a stage, or asks for stage exercises or examples.
---

# Stage handoff

Every stage of this project ends the same way, so the user (a Product Owner learning
RAG end to end) always knows where to look. This skill defines that shape.

## 1. Before writing code
Explain the concept in plain language: a few short paragraphs plus a small ASCII
diagram where it helps. Cover the trade-offs the brief in CLAUDE.md asks for.
Check the machine-dependent assumptions (RAM, models pulled) with the user or by
inspecting the machine. Never guess.

## 2. Build and verify
- Build only that stage's scope. Keep code simple and comment the *why*.
- **Run it for real.** Do not hand over a stage that has not been executed.
- If an earlier stage had to change, say what changed and why.

## 3. Default exercises (the part people get wrong)

Each stage has 2-3 "Try this" exercises. Every one of them ships with a **ready-to-run
default example** so the user never has to invent input.

### Content rules
- **Generic topics only.** Use everyday, neutral subject matter: geography, science
  basics, cooking, household, simple arithmetic, famous facts. **Never use trading,
  finance or any other personal domain** in exercise prompts or examples.
- **Verifiable ground truth.** Prefer questions with a known correct answer so the user
  can judge the result without trusting the model (capital cities, arithmetic, counts).
- **The example must actually demonstrate the concept.** Run it. If both models give the
  same answer, or the effect does not show, pick a different example. Do not ship an
  exercise whose point you have not observed.
- **Reproducible.** Pin `--temperature 0` in commands, and say outputs may still vary
  slightly across machines and versions.
- **Real output, labelled.** Paste output you captured, trimmed to the lines that matter,
  and label it "Example run (llama3.2:3b, temp 0)". Never invent or "expect-and-paste"
  output. If you could not run it, say so and mark it "expected, not run".
- **Corpus-based stages (2-6):** questions must be answerable from the sample notes in
  `docs/`. Keep question wording neutral, and include questions that are NOT in the notes.

### Fixed format for every exercise

```
### Exercise N: <short name>
**Goal:** one sentence: what concept this makes visible.
**Command:** exact command, in a code block.
**Type these:** the exact inputs, in order, in a code block.
**Watch for:** 2-3 bullet points (what to observe, where to look in the output).
**Example run:** real captured output (trimmed) or a small table.
**Why it happens:** 1-3 sentences linking back to the concept.
**Your turn:** one variation for the user to try with their own input.
```

## 4. Write the stage note
Copy [template.md](template.md) to `stages/stage-<N>-<slug>.md` in the project root and fill
every section. This file is the durable, standard record of the stage. Keep headings and
their order exactly as in the template. (Do **not** put these in `docs/`: that folder holds
the notes the user ingests into the RAG index.)

## 5. Update project files
- `README.md`: add or update the stage's section (run commands, key idea, link to the
  stage note) and any new prerequisites (models, packages).
- `CLAUDE.md`: update the **Progress** block (stage done, next stage, decisions made).

## 6. Hand over
- Reply with the standard handoff: what was built, how to run it, the stage note path, a
  short "What you just learned", and the exercises. Link the files, do not dump whole files.
- **Show the user first. Do not `git commit`, `git push` or open a PR unless the user asks.**
  Mention which files are new or modified so they can review.
- End with: say **"next"** to continue to Stage N+1. Then stop and wait.
