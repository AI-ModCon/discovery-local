---
# ---------------------------------------------------------------------------
# RESOURCE CARD TEMPLATE  (facilities, instruments, compute)
#
# Note the card_type is "infrastructure" while the registry endpoint is
# "resource_card". That is deliberate and not a typo.
#   curl -X POST http://localhost:18100/api/current/registry/resource_card \
#     -H "Content-Type: text/vnd.genesis.resource-card+markdown" \
#     --data-binary @resource_card.md
# ---------------------------------------------------------------------------
xCard:
  card_type: infrastructure
  version: '0.1'

id: my-example-resource
name: My Example Resource
description: >-
  An example facility or instrument. Replace this with what the resource is,
  what it measures or computes, and who may use it.

science:
  - accelerator-physics
keywords:
  - example
  - template
sensitivity: unreviewed
developed_by:
  - Your Organization
version: '0.1.0'
last_updated: '2026-10-05'
license:
  spdx_id: NOASSERTION
  name: ''
  url: ''
relationships: []

extension:
  kind: infrastructure
  # Exactly one of: compute, network, storage, instrument, service. CHANGE ME.
  resource_class: instrument
  # The facility this belongs to. CHANGE ME.
  facility: Your Facility
  # IRI/URN identifier if the resource has one, otherwise leave empty.
  iri_urn: ''
  # What it can do, one phrase each. CHANGE ME.
  capabilities:
    - Describe a capability this resource provides
  # A mapping of name to value. Keep the units in the name or the value, since a
  # number on its own is not a measurement. Leave as {} rather than guessing.
  quantitative_values:
    beam_energy_gev: 12
  # How a user reaches it: a scheme, endpoint or procedure.
  access_protocol: ''
  configuration: {}
---

# My Example Resource

Replace this body with what a user needs: where it is, how to request access,
what the operating constraints are.

## Capabilities

## Access

## Constraints
