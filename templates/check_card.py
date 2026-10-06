#!/usr/bin/env python3
"""Check a card before you register it, so you do not publish the template.

The templates are valid cards. That is deliberate, because it means you can
register one and watch the whole loop work. It also means the registry will
happily accept one you never edited: it is well formed, it just describes
nothing. A corpus of "My Example Agent" entries is worse than an empty one,
because search returns them.

Rather than keep a list of placeholder strings, which drifts the moment a
template changes, this compares your card against the template for its type
and reports every value that is still identical. If you meant to keep one, say
so with --allow, and the file records that you decided rather than forgot.

    python3 check_card.py my-agent.md
    python3 check_card.py my-agent.md --allow sensitivity --allow license
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - depends on the user's machine
    sys.exit("This needs PyYAML: pip install pyyaml")

HERE = Path(__file__).resolve().parent

TEMPLATE_FOR_TYPE = {
    "agent": "agent_card.md",
    "model": "model_card.md",
    "data": "data_card.md",
    "infrastructure": "resource_card.md",
}

# Prose the templates ship with. Leaving it in means the body was never written.
BODY_SENTINELS = (
    "Replace this body",
    "A paragraph or two.",
    "Replace this with what",
    "Describe one thing your agent can do",
)



# Fields that identify the thing. Matching the template here means the card has
# not been given an identity, whatever else was edited.
IDENTITY_FIELDS = {"id", "name", "description", "developed_by", "science", "keywords"}

# Fields that are supposed to match: the discriminator and the extension's own
# kind are fixed per card type, so reporting them would be noise.
STRUCTURAL_PREFIXES = ("xCard", "extension.kind")


def is_worth_flagging(path: str, value: Any) -> bool:
    """Is an unchanged value evidence of an unedited card?

    Identity fields always are. Beyond those, only prose: a shared enum, mime
    type or boolean says nothing about effort, and flagging "sensitivity:
    unreviewed" trains people to ignore the output.
    """
    if path.startswith(STRUCTURAL_PREFIXES):
        return False
    if path.split("[")[0].split(".")[0] in IDENTITY_FIELDS:
        return True
    return isinstance(value, str) and " " in value.strip() and len(value) > 20


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Return the parsed YAML front matter and the Markdown body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if match is None:
        sys.exit("No YAML front matter found: a card starts with a --- line.")
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        sys.exit(f"The front matter is not valid YAML:\n{exc}")
    if not isinstance(data, dict):
        sys.exit("The front matter should be a mapping of fields.")
    return data, match.group(2)


def leaves(node: Any, path: str = "") -> dict[str, Any]:
    """Flatten to {dotted.path: value} so two cards can be compared field by field."""
    found: dict[str, Any] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            found.update(leaves(value, f"{path}.{key}" if path else str(key)))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.update(leaves(value, f"{path}[{index}]"))
    elif node not in (None, "", [], {}):
        found[path] = node
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path, help="the card you are about to register")
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="FIELD",
        help="keep this field's template value on purpose (repeatable)",
    )
    args = parser.parse_args()

    if not args.card.is_file():
        sys.exit(f"No such file: {args.card}")

    card, body = split_front_matter(args.card.read_text(encoding="utf-8"))
    card_type = (card.get("xCard") or {}).get("card_type")
    template_name = TEMPLATE_FOR_TYPE.get(card_type)
    if template_name is None:
        sys.exit(
            f"xCard.card_type is {card_type!r}; expected one of "
            f"{', '.join(sorted(TEMPLATE_FOR_TYPE))}."
        )

    template_path = HERE / template_name
    if not template_path.is_file():
        sys.exit(f"Cannot find the template to compare against: {template_path}")
    template, _ = split_front_matter(template_path.read_text(encoding="utf-8"))

    card_leaves, template_leaves = leaves(card), leaves(template)
    allowed = set(args.allow)
    unchanged = [
        (path, value)
        for path, value in card_leaves.items()
        if path in template_leaves
        and template_leaves[path] == value
        and is_worth_flagging(path, value)
        and path.split("[")[0] not in allowed
        and path not in allowed
    ]

    stale_body = [s for s in BODY_SENTINELS if s in body]

    if not unchanged and not stale_body:
        print(f"{args.card}: ready to register.")
        return 0

    print(f"{args.card}: still carries template content.\n")
    if unchanged:
        print(f"Fields identical to {template_name}:")
        width = max(len(p) for p, _ in unchanged)
        for path, value in sorted(unchanged):
            shown = str(value)
            if len(shown) > 58:
                shown = shown[:55] + "..."
            print(f"  {path:<{width}}  {shown}")
        print()
    if stale_body:
        print("The body below the front matter is still the template's:")
        for sentinel in stale_body:
            print(f"  ...{sentinel}...")
        print()
    print(
        "Edit those, or pass --allow FIELD for any you mean to keep.\n"
        "A card that describes nothing is worse than no card: search returns it."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
