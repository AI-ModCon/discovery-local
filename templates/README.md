# Card templates

Five templates, one per card type. Each one is a **valid card already**: fill in
the values marked `CHANGE ME` and leave the structure alone. They are tested
against the registry on every change, so if yours is rejected it is something
you edited, not the template.

| file | register as | content type |
|---|---|---|
| `data_card.md` | `data_card` | `text/vnd.genesis.data-card+markdown` |
| `model_card.md` | `model_card` | `text/vnd.genesis.model-card+markdown` |
| `agent_card.md` | `agent_card` | `text/vnd.genesis.agent-card+markdown` |
| `resource_card.md` | `resource_card` | `text/vnd.genesis.resource-card+markdown` |
| `workflow_card.md` | *not registrable* | — |

The workflow card is the odd one. The registry recognises the four subtypes
above and workflow is not among them, so `seed_registry.py` skips workflow
cards the way it skips framework cards. The engine understands the type; only
registration has nowhere to put it. Load one through the storage path the
hackathon materials use -- the template says how at the top.

## The loop

```bash
# 1. take a copy. Leave the template alone so you can start again.
cp templates/agent_card.md my-agent.md

# 2. edit my-agent.md: replace every value marked CHANGE ME, and replace the
#    body below the frontmatter with your own documentation.

# 3. check you actually filled it in
python3 templates/check_card.py my-agent.md

# 4. register your copy
curl -X POST http://localhost:18100/api/current/registry/agent_card \
  -H "Content-Type: text/vnd.genesis.agent-card+markdown" \
  --data-binary @my-agent.md

# 5. tell the engine to pick it up
curl -X POST http://localhost:18000/api/v1/admin/resync

# 6. find it at http://localhost:15173
```

Keep your copy. The card you registered lives in the registry's storage, and
`docker compose down -v` discards it; your file is the only thing you can
re-register from.

Step 3 compares your card against the template it came from and refuses any
field you left untouched. The templates are valid cards, so the registry will
accept one you never edited: it is well formed, it just describes nothing. A
corpus full of "My Example Agent" is worse than an empty one, because search
returns them. Pass `--allow FIELD` for anything you mean to keep.

Without step 5 the card sits in the registry but is not searchable, because the
index is built when the engine starts.

Register the same file again after editing it and you get a **second card**, not
an updated one: the registry assigns a new id per submission. Change the `id:`
in your frontmatter when you mean a different card, and expect duplicates when
you are iterating.

You can also register through the registry's own API docs page at
http://localhost:18100/api/current/docs, which shows validation errors inline.
That is usually the better first experience.

## Two naming quirks that are not typos

**The resource card's `card_type` is `infrastructure`** while its endpoint is
`resource_card`. The engine models facilities and instruments as infrastructure;
the registry calls that subtype a resource card.

**The data card's `card_type` is `data`** while its endpoint is `data_card`, and
the Genesis data card v2 schema spells it `dataset`. The registry accepts `data`
today. Which spelling wins is being reconciled between the two schemas, so for
now follow the template.

## What the data card template is

Its `extension:` block is a **Genesis data card v2.0.0**, unchanged, built from
the working group's own minimum valid example. That half follows their field
reference guide. Everything above it is the xCard spine, which is what the
engine indexes and what lets a dataset, a model and an agent appear in one
search result.

The template declares only the discoverability and accessibility tiers, which is
the minimum that validates. Set another `supports_*` flag to `Yes` and add the
matching block when you have more to declare: `interoperability` for formats and
schema, `reusability` for licence and quality, `governed_use` for access and
review, `ai_usability` for training permissions.

## Writing a description that search can find

The `description` is what semantic search matches against. Write it for a
person: what the thing is, what it is for, what makes it different. "Surrogate
model predicting radiation from SRF cavity gradients" is findable. "Model v2
final" is not.
