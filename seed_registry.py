#!/usr/bin/env python
"""Push the bundled xCard corpus into a local registry, once.

Runs as a one-shot compose service before the engine starts, so the engine has
something to index. Deliberately uses the engine's own registry client rather
than raw HTTP: seeding then exercises the same create path the cluster
deployment uses, and a contract change breaks the local stack loudly instead of
silently diverging.

Uses durable operation keys across repeated uploads. Legacy bucket checks
without a ledger fail closed; populated stores need reviewed migration.

Historical behavior skipped populated buckets. The Registry assigns IDs, so
re-running would add a second copy of every card rather than updating them.
That did not show while the S3 stand-in discarded its files on shutdown, since
every start began empty. Now that it retains them, seeding has to check.

Set SEED_FORCE=1 to seed anyway, or `docker compose down -v` to start empty.
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
from genesis.knowledge._seed_state import seed_operation

CORPUS = Path(os.environ.get("SEED_CORPUS", "/app/cards/xcard"))
LIMIT = int(os.environ.get("SEED_LIMIT", "0"))
REGISTRY_URL = os.environ.get("XCARD_REGISTRY_URL", "http://registry:8000")
READY_ATTEMPTS = 60
FORCE = os.environ.get("SEED_FORCE", "") not in ("", "0", "false", "False")


def bucket_already_seeded() -> bool:
    """True when the registry's bucket already holds objects.

    Checked directly against storage rather than through the registry, which
    serves cards by id only and so cannot answer "is there anything here".
    Failure blocks first-run bootstrap without a ledger. Existing operation
    keys make subsequent runs independent of this bucket probe.
    """
    try:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=os.environ.get("XCARD_STORAGE_ENDPOINT_URL"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        listing = client.list_objects_v2(
            Bucket=os.environ["XCARD_STORAGE_BUCKET"],
            Prefix=os.environ.get("XCARD_STORAGE_PREFIX", ""),
            MaxKeys=1,
        )
        return listing.get("KeyCount", 0) > 0
    except Exception as exc:
        raise RuntimeError(
            "Could not establish whether legacy Registry data exists"
        ) from exc


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
    # Registry idempotency, not bucket enumeration, determines repeat safety.
    # FORCE never discards keys. The ledger must survive container restarts.
    state_path = Path(os.environ.get("SEED_STATE_PATH", "/seed-state/operations.json"))
    if not state_path.exists():
        try:
            if bucket_already_seeded():
                print(
                    "Registry has data but no seed ledger. "
                    "Review legacy seed migration; refusing fresh keys.",
                    file=sys.stderr,
                )
                return 1
        except RuntimeError:
            print(
                "Bucket check unavailable and no seed ledger; refusing fresh keys.",
                file=sys.stderr,
            )
            return 1

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
                with seed_operation(
                    Path(
                        os.environ.get("SEED_STATE_PATH", "/seed-state/operations.json")
                    ),
                    target=REGISTRY_URL,
                    caller=os.environ.get("SEED_CALLER_SCOPE", "local-permissive-user"),
                    source=path.relative_to(CORPUS).as_posix(),
                    xcard_type=xcard_type,
                    content=markdown.encode("utf-8"),
                ) as key:
                    await client.create_card(
                        markdown, xcard_type=xcard_type, idempotency_key=key
                    )
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

    # A failed operation needs investigation, even when other cards succeeded.
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
