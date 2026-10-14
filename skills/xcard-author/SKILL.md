---
name: xcard-author
description: "Write an xCard for the Genesis Discovery Engine and register it: model, data, agent, resource or workflow. Use when the user wants to describe a model, dataset, agent, facility, instrument or pipeline as a card, add something to the Discovery Engine or the xCard Registry, fix a card the registry rejected, or asks what a card needs. Starts from templates that are tested against the real registry, fills them by asking and by reading the artefact, checks the card has actually been edited, and registers it."
compatibility: "Needs the local Genesis stack running (docker compose up) to validate and register. Without it, the card can still be written and checked, just not registered."
allowed-tools: Bash(*) Read Write Edit Glob Grep
---

# Writing an xCard

An xCard describes one thing -- a model, a dataset, an agent, a facility, a
workflow -- so that the Discovery Engine can find it and the assistant can
answer questions about it. This skill writes one, checks it, and registers it.

**Do not write a card from scratch.** Start from the template for its type.
The templates in `assets/` are valid cards already and are tested against the
registry, so a rejection means something was edited wrongly, not that the
shape is wrong. Writing the YAML freehand reproduces, slowly, every mistake
the templates already encode.

## Workflow

```
Progress:
- [ ] 1. Decide the type, and read what it costs you (below)
- [ ] 2. Copy the template; never edit the template in place
- [ ] 3. Learn about the thing before asking the user about it
- [ ] 4. Fill the front matter, then the body
- [ ] 5. Check it with scripts/check_card.py
- [ ] 6. Validate against the registry
- [ ] 7. Register it, resync, and confirm search finds it
```

## 1. Decide the type

| the thing is | type | template | registers as |
|---|---|---|---|
| a trained model | `model` | `model_card.md` | `model_card` |
| a dataset | `data` | `data_card.md` | `data_card` |
| something that acts, with tools | `agent` | `agent_card.md` | `agent_card` |
| a facility, instrument or compute | `infrastructure` | `resource_card.md` | `resource_card` |
| a pipeline of steps | `workflow` | `workflow_card.md` | **cannot be registered** |

Two of those rows are traps, and both are deliberate rather than bugs:

- **A resource card's `card_type` is `infrastructure`**, while its endpoint is
  `resource_card`. The names do not match and both are correct.
- **A workflow card cannot go through the registry at all.** The registry
  knows four subtypes and workflow is not one, so `seed_registry.py` skips
  them like framework cards. Load it by writing to storage directly --
  see step 7.

If the user is describing several things, write several cards. A card that
describes a model *and* its dataset is findable as neither.

## 2. Copy the template

```bash
cp assets/agent_card.md my-agent.md
```

Leave the template alone so the user can start again, and so
`check_card.py` still has something to compare against.

## 3. Learn before you ask

Ask the user only what you cannot find out. Before asking, look:

- a repository: `README`, `pyproject.toml`, `setup.py`, `LICENSE`, `Makefile`
- a model: a `config.json`, a model card on a hub, training scripts
- a dataset: the directory, file formats, sizes, a manifest
- an existing card for the same project, if there is one

Then ask for what is genuinely only in someone's head: who owns it, who may
use it, what it is for, what it must not be used for, and what it has not been
tested on. Ask in small batches, not as a questionnaire.

**Never invent a value.** An empty field is recoverable; a plausible wrong one
is not, because nobody will re-check it. If a field cannot be answered, leave
the template's value and tell the user which ones you left.

## 4. Fill it in

Front matter first, then the body.

**`description` is the field that matters most.** The engine indexes the
title, description, keywords and skills -- *not the body*. It falls back to
the body only when all of that is under 80 characters. So a card with a
one-line description and a rich body is searchable by that one line, and every
question about its content misses. Put what the thing does, in the words
someone would search for, in `description`.

**`keywords` is how a specific question reaches a specific card.** This corpus
has 300-odd cards competing on the same words; keywords are the tie-break.
Use plain terms a person would type. A keyword that is only digits (`2026`)
is rejected by the registry outright.

**`id`** is lowercase, hyphen or underscore separated, and stable. It is how
other cards refer to this one.

**`sensitivity`** decides who sees it. `general` is visible to everyone;
restricted values are filtered out for users without clearance, which looks
exactly like the card being missing.

Relationships are **derived from three fields and nothing else**:

| field | edge |
|---|---|
| `datasets:` (list) | `uses_dataset`, one per entry |
| `base_model:` | `derived_from` |
| `new_version:` | `superseded_by` |

A `relationships:` block in the front matter is **ignored by the parser** --
writing one creates no edges. Targets that resolve to no card are dropped, so
name only ids that exist:

```bash
curl -s localhost:18000/api/v1/cards/<id> | head -c 200
```

## 5. Check it

```bash
python3 scripts/check_card.py my-agent.md
```

This compares the card against its template and reports every value still
identical to it. The templates are valid cards, so the registry will happily
accept one that was never edited -- and a corpus of "My Example Agent" entries
is worse than an empty one, because search returns them.

If a template value is genuinely right, keep it deliberately:

```bash
python3 scripts/check_card.py my-agent.md --allow sensitivity --allow license
```

## 6. Validate against the registry

The registry is the real validator. Ask it before you commit to anything:

```bash
curl -s -X POST http://localhost:18100/api/current/registry/agent_card \
  -H "Content-Type: text/vnd.genesis.agent-card+markdown" \
  --data-binary @my-agent.md -w '\nHTTP %{http_code}\n'
```

Content types, which must match the endpoint:

| endpoint | content type |
|---|---|
| `data_card` | `text/vnd.genesis.data-card+markdown` |
| `model_card` | `text/vnd.genesis.model-card+markdown` |
| `agent_card` | `text/vnd.genesis.agent-card+markdown` |
| `resource_card` | `text/vnd.genesis.resource-card+markdown` |

A rejection names the field: `{"details":[{"path":["keywords",7], ...}]}`
means `keywords[7]`. Fix that field and send it again. Read the path rather
than guessing -- the message is precise and the guess usually is not.

## 7. Register, resync, confirm

A `201` means it is stored. The engine does not notice until it re-reads:

```bash
curl -X POST http://localhost:18000/api/v1/admin/resync
```

**For a workflow card**, which the registry cannot take, write it to storage
directly instead:

```bash
cp my-workflow.md hackathon/
docker compose exec api python /load_hackathon_materials.py
curl -X POST http://localhost:18000/api/v1/admin/resync
```

Then confirm it is actually findable, which is the only evidence that any of
this worked:

```bash
curl -s -X POST http://localhost:18000/api/v1/discover \
  -H 'Content-Type: application/json' \
  -d '{"query":"<something only this card answers>","limit":5}' \
  | python3 -m json.tool | head -30
```

If the card does not come back, the usual causes in order: the resync was not
run; the distinguishing words are in the body rather than the description;
`sensitivity` is restricted; or the words you searched do not appear in the
card at all.

## When the user wants to fix a rejected card

Read the error's `path` and change that field only. Do not rewrite the card:
the rest of it passed. If the same card is rejected repeatedly, diff it
against the template for its type -- something structural has usually been
removed rather than something being wrong with a value.
