#!/usr/bin/env bash
# Register a card and prove it is findable.
#
# Registering is two steps and a type match, and getting any of them wrong
# fails quietly: the registry rejects a mismatched content type, the engine
# does not notice a new card until it resyncs, and a card that registered but
# is not indexed looks exactly like one that never registered at all. This
# does all three and tells you which part failed.
#
# It does not decide anything on your behalf. Registering stays something a
# person runs deliberately (ADR-0004): this is the same two calls the card
# builder prints, with the type read off the card instead of typed by hand,
# and a search afterwards so "it worked" is a thing you saw rather than
# assumed.
#
#   ./register_card.sh my-agent.md
#
set -euo pipefail

CARD="${1:-}"
REGISTRY="${REGISTRY_URL:-http://localhost:18100}"
ENGINE="${ENGINE_URL:-http://localhost:18000}"

[ -n "${CARD}" ] || { echo "usage: $0 <card.md>" >&2; exit 2; }
[ -f "${CARD}" ] || { echo "No such file: ${CARD}" >&2; exit 2; }

# The spine card_type, which is not always the registry's name for it.
card_type="$(sed -n '/^xCard:/,/^[a-z]/p' "${CARD}" \
  | sed -n 's/^[[:space:]]*card_type:[[:space:]]*//p' | head -1 | tr -d '"'"'"' ')"
[ -n "${card_type}" ] || { echo "No xCard.card_type in ${CARD}; is it a card?" >&2; exit 2; }

case "${card_type}" in
  data)           subtype=data_card;     media=data-card ;;
  model)          subtype=model_card;    media=model-card ;;
  agent)          subtype=agent_card;    media=agent-card ;;
  infrastructure) subtype=resource_card; media=resource-card ;;
  workflow|framework)
    cat >&2 <<EOF
${CARD} is a ${card_type} card, and the registry has no subtype for it -- it
knows data_card, model_card, agent_card and resource_card and nothing else.
Load it through the registry's storage instead:

  cp "${CARD}" hackathon/
  docker compose exec api python /load_hackathon_materials.py
  curl -X POST ${ENGINE}/api/v1/admin/resync
EOF
    exit 2 ;;
  *) echo "Unknown card_type '${card_type}' in ${CARD}" >&2; exit 2 ;;
esac

card_id="$(sed -n 's/^id:[[:space:]]*//p' "${CARD}" | head -1 | tr -d '"'"'"' ')"

echo "==> registering ${CARD} as ${subtype}"
body="$(mktemp)"; trap 'rm -f "${body}"' EXIT
code="$(curl -sS -o "${body}" -w '%{http_code}' -X POST \
  "${REGISTRY}/api/current/registry/${subtype}" \
  -H "Content-Type: text/vnd.genesis.${media}+markdown" \
  --data-binary @"${CARD}")"

if [ "${code}" != "201" ]; then
  echo "    the registry refused it (HTTP ${code}):" >&2
  # The error names the field; print it rather than making someone read JSON.
  python3 - "${body}" >&2 <<'PY' || cat "${body}" >&2
import json, sys
d = json.load(open(sys.argv[1]))
print("   ", d.get("message", "")) if d.get("message") else None
for item in d.get("details", []):
    where = ".".join(str(p) for p in item.get("path", [])) or "(card)"
    print(f"      {where}: {item.get('message','')}")
PY
  exit 1
fi
echo "    registered"

echo "==> telling the engine to re-read the registry"
curl -sS -X POST "${ENGINE}/api/v1/admin/resync" >/dev/null
echo "    resynced"

# The only evidence that any of it worked.
echo "==> checking it is findable"
found="$(curl -sS "${ENGINE}/api/v1/cards/${card_id}" -o /dev/null -w '%{http_code}' || true)"
if [ "${found}" = "200" ]; then
  echo "    ${card_id} is in the engine"
  echo
  echo "Search for it at ${ENGINE%:*}:15173, or:"
  echo "  curl -s -X POST ${ENGINE}/api/v1/discover -H 'Content-Type: application/json' \\"
  echo "    -d '{\"query\":\"<words only this card answers>\",\"limit\":5}'"
else
  cat >&2 <<EOF
    registered, but the engine does not serve ${card_id} (HTTP ${found}).

    Usually one of:
      - the card's id is not what this script read from it
      - sensitivity is restricted, so it is filtered out for you
      - the engine is still indexing; try the resync again in a moment
EOF
  exit 1
fi
