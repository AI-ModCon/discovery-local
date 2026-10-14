---
# ---------------------------------------------------------------------------
# WORKFLOW CARD TEMPLATE  (a pipeline of steps, each one a card)
#
# Two things about this type are different from the other four, and both will
# catch you out if you assume otherwise.
#
# 1. IT DOES NOT GO THROUGH THE REGISTRY. The registry recognises four
#    subtypes -- data_card, model_card, agent_card, resource_card -- and
#    workflow is not one of them, so seed_registry.py skips workflow cards the
#    way it skips framework cards. The engine understands the type; only
#    registration has nowhere to put it. Load it by writing it to the
#    registry's storage directly:
#
#      cp workflow_card.md ../hackathon/my-workflow.md
#      docker compose exec api python /load_hackathon_materials.py
#      curl -X POST http://localhost:18000/api/v1/admin/resync
#
# 2. THE BODY IS NOT INDEXED. searchable_text reads the title, description,
#    keywords and skills, and only falls back to the body when all of that is
#    under 80 characters. A card with a one-line description and the steps
#    written out below will be searchable by that one line, and every question
#    about the steps will miss it. So the description carries the workflow:
#    write it out there, and keep the body as the readable version.
#
# A workflow card has no extension block -- there is no workflow extension in
# the schema. It carries the spine and nothing else.
# ---------------------------------------------------------------------------
xCard:
  card_type: workflow
  version: '0.1'

id: my-example-workflow
name: My Example Workflow

# CHANGE ME. Long on purpose: this is what the engine indexes, so anything a
# person might ask about the workflow has to appear here, including the steps
# and what each one runs.
description: |-
  An example workflow. Replace this with what the workflow produces, what it
  starts from, and who would run it, in the words someone would search for.

  Steps:
  1. Name the step, the card that performs it, and what it takes in.
  2. Name the next one, what it produces, and what the step after it needs.

  Inputs: the data, accounts and access you must have before starting.
  Outputs: what you are left with, and where it lands.

science:
  - computer-science
keywords:
  - example
  - template
sensitivity: unreviewed
developed_by:
  - Your Organization
version: '0.1.0'
last_updated: '2026-10-14'
license:
  spdx_id: NOASSERTION
  name: ''
  url: ''

# The engine builds relationships from three fields and ignores anything else,
# including a `relationships:` list -- writing one does not create edges.
#   datasets:    -> uses_dataset, one edge per entry
#   base_model:  -> derived_from
#   new_version: -> superseded_by
# Name only cards that exist; a target that resolves to nothing is dropped.
# Check one with: curl -s localhost:18000/api/v1/cards/<id> | head -c 200
datasets: []
relationships: []
---

# My Example Workflow

The readable version of what the description says. Keep them in step: the
description is what search reads, this is what a person reads once they have
found it.

## Steps

1. **Name the step** -- which card performs it, and what it takes in.
2. **Name the next one** -- what it produces, and what the next step needs.

## Inputs

What you must have before you start: the data, the accounts, the access.

## Outputs

What you are left with, and where it lands.

## Caveats

Where this breaks, what it assumes, and what it has not been tried on.
