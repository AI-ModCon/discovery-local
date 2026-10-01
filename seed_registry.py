#!/usr/bin/env python
"""Push the bundled xCard corpus into a local registry, once.

Runs as a one-shot compose service before the engine starts, so the engine has
something to index. Deliberately uses the engine's own registry client rather
than raw HTTP: seeding then exercises the same create path the cluster
deployment uses, and a contract change breaks the local stack loudly instead of
silently diverging.

Idempotent by omission rather than by design: the registry assigns ids, so
re-running adds duplicates. Compose only runs it once per `up`; use
`docker compose down -v` to start from an empty bucket.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import yaml

from genesis.knowledge._registry_api_client import (
    CARD_TYPE_TO_XCARD_TYPE,
    RegistryApiConfig,
    RegistryApiError,
    XCardRegistryApiClient,
)

CORPUS = Path(os.environ.get("SEED_CORPUS", "/app/cards/xcard"))
LIMIT = int(os.environ.get("SEED_LIMIT", "0"))
REGISTRY_URL = os.environ.get("XCARD_REGISTRY_URL", "http://registry:8000")
READY_ATTEMPTS = 60


def card_type_of(markdown: str) -> str | None:
    """The spine card_type, or None if this file is not an xCard."""
    if not markdown.startswith("---"):
        return None
    end = markdown.find("\n---", 3)
    if end < 0:
        return None
    try:
        front = yaml.safe_load(markdown[3:end])
    except yaml.YAMLError:
        return None
    if not isinstance(front, dict):
        return None
    return (front.get("xCard") or {}).get("card_type")


async def wait_for_registry(client: XCardRegistryApiClient) -> bool:
    for attempt in range(READY_ATTEMPTS):
        if await client.ready():
            return True
        await asyncio.sleep(2)
        if attempt and attempt % 10 == 0:
            print(f"  still waiting for the registry ({attempt * 2}s)", flush=True)
    return False


async def main() -> int:
    paths = sorted(CORPUS.rglob("*.md"))
    if LIMIT:
        paths = paths[:LIMIT]
    if not paths:
        print(f"no cards under {CORPUS}; nothing to seed", file=sys.stderr)
        return 0

    client = XCardRegistryApiClient(RegistryApiConfig(base_url=REGISTRY_URL))
    async with client:
        if not await wait_for_registry(client):
            print(f"registry at {REGISTRY_URL} never became ready", file=sys.stderr)
            return 1

        created = 0
        unsupported: dict[str, int] = {}
        failed: list[str] = []

        for path in paths:
            markdown = path.read_text(encoding="utf-8", errors="replace")
            card_type = card_type_of(markdown)
            xcard_type = CARD_TYPE_TO_XCARD_TYPE.get(str(card_type))
            if xcard_type is None:
                # framework and workflow cards have no registry subtype
                unsupported[str(card_type)] = unsupported.get(str(card_type), 0) + 1
                continue
            try:
                await client.create_card(markdown, xcard_type=xcard_type)
                created += 1
            except RegistryApiError as exc:
                failed.append(f"{path.name}: {exc.code} {exc.message}"[:160])
            except Exception as exc:  # noqa: BLE001 - seeding is best effort
                failed.append(f"{path.name}: {type(exc).__name__} {exc}"[:160])

        print(f"seeded {created}/{len(paths)} cards into {REGISTRY_URL}", flush=True)
        if unsupported:
            print(f"  skipped, no registry subtype: {unsupported}", flush=True)
        if failed:
            print(f"  failed: {len(failed)}", flush=True)
            for line in failed[:10]:
                print(f"    {line}", flush=True)

    # A partial seed still leaves a usable stack, so only a total failure is fatal.
    return 0 if created else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
