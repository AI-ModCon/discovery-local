---
# ---------------------------------------------------------------------------
# DATA CARD TEMPLATE
#
# The block under `extension:` is a Genesis data card v2.0.0, unchanged. That
# half is owned by the data card working group: fill it the way their field
# reference guide describes. The fields above it are the xCard spine, which is
# what the engine indexes and what lets a dataset, a model and an agent sit in
# one search result.
#
# This is the minimum that validates. Set a supports_* flag to "Yes" and add
# the matching block when you have more to declare: interoperability for
# formats and schema, reusability for licence and quality, governed_use for
# access and review, ai_usability for training permissions.
#
# Replace every value marked CHANGE ME. Register with:
#   curl -X POST http://localhost:18100/api/current/registry/data_card \
#     -H "Content-Type: text/vnd.genesis.data-card+markdown" \
#     --data-binary @data_card.md
# ---------------------------------------------------------------------------

# --- xCard spine ------------------------------------------------------------
# card_type is "data" here while the registry endpoint is "data_card". That is
# deliberate, and the two spellings are a known disagreement: Genesis data card
# v2.0.0 fixes card_type to "dataset", the spine enumerates "data". The local
# registry now accepts either, so a card written against the published schema
# registers unchanged. "data" stays canonical until the schemas are reconciled.
xCard:
  card_type: data
  version: '0.1'
id: my-example-dataset                      # CHANGE ME: lowercase, hyphens
name: My Example Dataset                    # CHANGE ME
description: >-                             # CHANGE ME
  Replace this with what the data contains, how it was collected and what it is
  useful for. Keep it in step with dataset_summary below.
science:                                    # CHANGE ME
  - accelerator-physics
keywords:
  - example
  - template
sensitivity: unreviewed
developed_by:                               # CHANGE ME
  - Your Organization
version: '0.1.0'
last_updated: '2026-10-05'                  # CHANGE ME
io_contract:
  input_modes: []
  output_modes: []
  modalities: []
  task_tags: []
  dataset_role: final
relationships: []

# --- Genesis data card v2.0.0, as the data extension ------------------------
extension:
  supports_discoverability: 'Yes'
  supports_accessibility: 'Yes'
  supports_interoperability: 'No'
  supports_reusability: 'No'
  supports_governed_use: 'No'
  supports_ai_usability: 'No'
  discoverability:
    datacard:
      template_version: 2.0.0
      datacard_version: 1.0.0
      filename: data_card.md
      language: en
      id:
        type: unregistered
        value: n/a
      sensitivity:
        overall_sensitivity: Public
        source_marking_string: not_applicable
        source_marking_scheme: None
        classified_status: 'No'
        cui_status: 'No'
        ucni_status: 'No'
      creation_method: Manual
      created_date: '2026-03-10'
      updated_date: '2026-05-11'
      change_log:
      - change_date: '2026-03-10'
        datacard_version: 1.0.0
        summary: Initial creation
      created_by:
      - contribution_date: '2026-03-10'
        description: Initial creation of datacard template and population with information
          about the dataset.
        creator:
          person:
            given_name: Your
            family_name: Name
            orcid: https://orcid.org/0000-0000-0000-0000
            email: you@example.org
            affiliation: &id001
              name: Your Organization
              ror_id: ''
            role: &id002
            - Data_Curator
    identification:
      name: My Example Dataset
      project: genesis
      version: 1.0.0
      primary_id:
        type: unregistered
        value: n/a
    dataset_description:
      dataset_summary: Replace this with what the data contains, how it was collected and
        what it is useful for. This is what semantic search matches against, so write it for
        a reader.
      keywords:
      - example
      - template
    product_type: Dataset
    release_status: Draft
    contact:
    - person:
        given_name: Your
        family_name: Name
        orcid: https://orcid.org/0000-0000-0000-0000
        email: you@example.org
        affiliation: *id001
        role: *id002
    authors:
    - person:
        given_name: Your
        family_name: Name
        orcid: https://orcid.org/0000-0000-0000-0000
        email: you@example.org
        affiliation: *id001
        role: *id002
    sponsor_organizations:
    - name: Your Funding Source
    research_organizations:
    - name: Your Organization
      ror_id: ''
    sensitivity:
      overall_sensitivity: Public
      source_marking_string: not_applicable
      source_marking_scheme: None
      classified_status: 'No'
      cui_status: 'No'
      ucni_status: 'No'
    workflow:
      state: Raw
  accessibility:
    access_policy:
      access_level: Open
    access:
      current_location: 'CHANGE ME: a DOI, URL or bucket path'
---

# My Example Dataset

Replace this body with what a reader needs in order to decide whether this
dataset suits them, and then to use it.

## What the data contains

## How it was collected

## Structure and files

## Quality, gaps and known issues

## How to cite
