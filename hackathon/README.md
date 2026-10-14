# Hackathon materials

The agenda and the welcome packet for the Genesis Mission Hands-on Hackathon,
14-16 October 2026, as cards, so the assistant can answer the questions people
actually ask on the day: where lunch is, which building they are in, how to get
an ALCF account, what the wifi is, where to go if the fire alarm goes off.

They are event documents rather than cards about a resource, so they carry the
spine and no extension block, and their `card_type` is `hackathon_materials`.
The engine knows that type; the registry does not, and deliberately so -- a
subtype that exists for three days is not worth teaching it. `load_hackathon_
materials.py` writes them to the registry's storage directly, which is why
`seed_registry.py` leaves them alone.

To load them into a running local stack:

```bash
docker compose exec api python /load_hackathon_materials.py
curl -X POST http://localhost:18000/api/v1/admin/resync
```

Then "where is lunch?" in the assistant answers from the welcome packet.

## Why the whole document is in `description`

`searchable_text` indexes a card's title, description, tags and skills, and
falls back to the body only when that structured text is under 80 characters.
A card with a one-line summary and the document in its body would therefore be
indexed by its summary alone, and every question about the contents would miss.
So the full text goes in `description`, and the indexer chunks it.

That is also why the keyword list is long and plain -- `lunch`, `coffee`,
`wifi`, `shuttle`, `badge`. These two cards compete with 300-odd research cards
that match the same words harder (`NERSC` pulls the NERSC facility cards first),
and the keywords are what let a logistics question reach a logistics card.
`wifi` returned nothing from these cards until they were added.

## Regenerating them

They were converted from the `.docx` originals. If a document changes, convert
it again and keep the shape: full text in `description`, same `id` (the loader
derives a stable storage key from it, so a reload replaces rather than adds a
version), and `card_type: hackathon_materials`.
