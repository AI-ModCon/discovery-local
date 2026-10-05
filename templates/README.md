# Card templates

Four templates, one per card type. Each one is a **valid card already**: fill in
the values marked `CHANGE ME` and leave the structure alone. They are tested
against the registry on every change, so if yours is rejected it is something
you edited, not the template.

| file | register as | content type |
|---|---|---|
| `data_card.md` | `data_card` | `text/vnd.genesis.data-card+markdown` |
| `model_card.md` | `model_card` | `text/vnd.genesis.model-card+markdown` |
| `agent_card.md` | `agent_card` | `text/vnd.genesis.agent-card+markdown` |
| `resource_card.md` | `resource_card` | `text/vnd.genesis.resource-card+markdown` |

## The loop

```bash
# 1. register it
curl -X POST http://localhost:18100/api/current/registry/agent_card \
  -H "Content-Type: text/vnd.genesis.agent-card+markdown" \
  --data-binary @agent_card.md

# 2. tell the engine to pick it up
curl -X POST http://localhost:18000/api/v1/admin/resync

# 3. find it at http://localhost:15173
```

Without step 2 the card sits in the registry but is not searchable, because the
index is built when the engine starts.

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
