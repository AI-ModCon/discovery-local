#!/usr/bin/env python3
"""Load the hackathon's own documents into the local registry's storage.

The agenda and the welcome packet are cards so that the assistant can answer
from them, but they are not cards about a resource: they carry the spine and
nothing else, and their `card_type` is `hackathon_materials`, which the
registry has no subtype for. `seed_registry.py` skips them for exactly the
reason it skips framework and workflow cards -- there is no endpoint to POST
them to.

So they are written to the registry's storage directly, under a key shaped
like the ones the registry writes itself, and the engine picks them up on its
next sync because it lists the bucket rather than asking the registry what
exists. That bypasses the registry's validation, which is the point: this is a
local, event-scoped deployment, and the alternative is teaching the registry a
subtype that exists for three days.

Re-running this is safe. Each card keeps a fixed storage id derived from its
card id, so a second run replaces the same object rather than adding a version
-- which matters because the engine ingests every version it finds and keeps
whichever key sorts last.

    docker compose exec api python /load_hackathon_materials.py
    curl -X POST http://localhost:18000/api/v1/admin/resync
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

CARDS = Path(os.environ.get("HACKATHON_CARDS", "/hackathon"))
# The registry lays objects out as <prefix>/<subtype>/<card uuid>/versions/
# <n>-<version uuid>.md. Nothing reads the subtype segment back -- the engine
# parses the markdown -- so these sit under resource_card to keep the shape.
SUBTYPE = "resource_card"
# Any fixed namespace works; this one just has to stay the same between runs so
# a card keeps its key.
NAMESPACE = uuid.UUID("6f1b2c7e-4a3d-4f5b-9c2e-8d7a1b3c5e90")


def is_card(text: str) -> bool:
    """True when this file is an xCard rather than prose that lives beside one.

    Same shape of check `seed_registry.py` makes: front matter with a spine
    `xCard.card_type`. A README has neither.
    """
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end < 0:
        return False
    try:
        import yaml

        front = yaml.safe_load(text[3:end])
    except Exception:  # noqa: BLE001 - malformed front matter is not a card
        return False
    return isinstance(front, dict) and bool((front.get("xCard") or {}).get("card_type"))


def main() -> int:
    import boto3

    bucket = os.environ.get("XCARD_STORAGE_BUCKET")
    if not bucket:
        print("XCARD_STORAGE_BUCKET is unset; run this inside the api container", file=sys.stderr)
        return 1

    prefix = os.environ.get("XCARD_STORAGE_PREFIX", "registry").strip("/")
    client = boto3.client(
        "s3",
        endpoint_url=os.environ.get("XCARD_STORAGE_ENDPOINT_URL"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )

    # Only actual cards. The directory also holds its own README, and a
    # loader that uploads every .md it finds puts that README in the corpus
    # as a card -- which is how this was first written, and the engine
    # happily indexed it.
    paths = [p for p in sorted(CARDS.glob("*.md")) if is_card(p.read_text(encoding="utf-8"))]
    if not paths:
        print(f"no cards under {CARDS}", file=sys.stderr)
        return 1

    for path in paths:
        card_uuid = uuid.uuid5(NAMESPACE, path.stem)
        version_uuid = uuid.uuid5(NAMESPACE, f"{path.stem}:1")
        key = f"{prefix}/{SUBTYPE}/{card_uuid}/versions/1-{version_uuid}.md"
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=path.read_text(encoding="utf-8").encode("utf-8"),
            ContentType="text/markdown",
        )
        print(f"  {path.name} -> {key}")

    print(f"wrote {len(paths)} cards; resync the engine to index them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
