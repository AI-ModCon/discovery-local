---
# ---------------------------------------------------------------------------
# MODEL CARD TEMPLATE
#
# Replace every value marked CHANGE ME. Leave the structure alone.
#   curl -X POST http://localhost:18100/api/current/registry/model_card \
#     -H "Content-Type: text/vnd.genesis.model-card+markdown" \
#     --data-binary @model_card.md
# ---------------------------------------------------------------------------
xCard:
  card_type: model
  version: '0.1'

id: my-example-model
name: My Example Model
description: >-
  An example model that demonstrates the card format. Replace this with what
  the model predicts, what it was trained on and what it is useful for.

science:
  - materials
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

io_contract:
  input_modes:
    - text/csv
  output_modes:
    - text/csv
  modalities: []
  task_tags: []

extension:
  kind: model
  # How it was built. CHANGE ME.
  architecture: Describe the architecture, for example a 3-layer MLP
  framework: PyTorch
  base_model: ''
  # Datasets it was trained on. Use card ids where one exists, so the engine can
  # link the model to its data.
  training_datasets: []
  # Reported performance. Keep the units: a number without one is not a result.
  metrics:
    - name: RMSE
      value: '0.0'
      unit: ''
      dataset: ''
---

# My Example Model

Replace this body with documentation a reader needs: what the model does, how it
was trained and validated, and where it should not be trusted.

## Intended use

## Training data

## Evaluation

## Limitations and risks
