---
# ---------------------------------------------------------------------------
# AGENT CARD TEMPLATE
#
# Replace every value marked CHANGE ME. Leave the structure alone: the field
# names are the contract, and the registry rejects a card that drops one.
# Register it with:
#   curl -X POST http://localhost:18100/api/current/registry/agent_card \
#     -H "Content-Type: text/vnd.genesis.agent-card+markdown" \
#     --data-binary @agent_card.md
# ---------------------------------------------------------------------------
xCard:
  card_type: agent
  version: '0.1'

# A stable, unique id. Lowercase, hyphens, no spaces. CHANGE ME.
id: my-example-agent
# What a person sees in search results. CHANGE ME.
name: My Example Agent
# One or two sentences: what it does and who it is for. This is what semantic
# search matches against, so write it for a reader, not a parser. CHANGE ME.
description: >-
  An example agent that demonstrates the card format. Replace this with a
  description of what your agent does, what problem it solves and what a user
  can expect from it.

# Science domains, lowercase. Required for agent cards. CHANGE ME.
science:
  - ai_co_scientist
# Free keywords that should find this card. CHANGE ME.
keywords:
  - example
  - template
# One of: unreviewed, general, reviewed, restricted.
sensitivity: unreviewed
# Organisations or teams. Required for agent cards. CHANGE ME.
developed_by:
  - Your Organization
version: '0.1.0'
last_updated: '2026-10-05'
license:
  spdx_id: NOASSERTION
  name: ''
  url: ''
relationships: []

# What the agent consumes and produces. Used to check whether two cards can be
# chained in a workflow, so keep it honest.
io_contract:
  input_modes:
    - text/plain
  output_modes:
    - text/plain
  modalities: []
  task_tags: []

extension:
  kind: agent
  # Short phrases, one per capability. CHANGE ME.
  skills:
    - Describe one thing your agent can do
  capabilities:
    streaming: false
    push_notifications: false
    state_transition_history: false
  protocol_version: ''
---

# My Example Agent

Replace this body with the human-readable documentation for your agent. The
frontmatter above is what the engine indexes and reasons over; this part is what
someone reads once they have found it.

## What it does

A paragraph or two.

## How to use it

Endpoint, invocation, authentication, whatever a user needs to actually run it.

## Limitations

What it does not do, and where it should not be relied on.
