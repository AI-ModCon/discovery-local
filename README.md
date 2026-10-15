# Discovery Engine + xCard Registry, on your laptop

The engine and the real AmSC xCard Registry running together locally. No AmSC
account, no VPN, no AWS. You can register a card through the registry and find
it in engine search.

One exception, and only one: the workflow assistant calls a language model
through the AmSC Model Access Gateway, which needs an AmSC account and, from
what we have seen, the AmSC network. Everything else here works offline.

Every service here is the same image that runs on the cluster. Only what sits
underneath them changes.

## Before you start

You need no AmSC account, no GitLab account, no AWS credentials and no VPN --
except for the workflow assistant, which is the one feature that calls out to a
language model. You do need the following, and it is worth checking all six
rather than discovering them one failure at a time.

**A supported platform.** The published images are multi-architecture, so
`docker compose pull` resolves `linux/amd64` or `linux/arm64` to match your
machine and there is nothing for you to choose. That covers Intel and AMD,
Apple Silicon, and Windows, where Docker Desktop runs these Linux containers
through WSL2.

The tarball route is the exception: a tarball carries one architecture, whichever
the machine that built it had. If you were handed one and the containers exit
immediately with `exec format error`, it was built for the other architecture.
Check what you are on with:

```bash
docker version --format '{{.Server.Arch}}'
```

which works in PowerShell as well as in a shell, unlike `uname -m`.

**Docker, with Compose v2.** Check with:

```bash
docker compose version
```

That must report `v2.x`. The older standalone `docker-compose` will not work:
this stack uses `depends_on` conditions that only v2 understands.

**At least 6GB of memory available to Docker.** OpenSearch, the engine with its
embedding model, the registry and the S3 stand-in run at once. Docker Desktop's
default allocation has been as low as 2GB on some installs, so check rather than
assume: Settings, then Resources. Too little memory shows up as OpenSearch
exiting on its own partway through startup, which does not look like an
out-of-memory error.

**About 8GB of free disk.** The images are roughly 4GB once loaded, plus the
volumes and the embedding model on top.

**On native Linux Docker, `vm.max_map_count` raised.** OpenSearch refuses to
start below 262144 and says so in its logs. Docker Desktop on macOS and Windows
already sets this, so this applies only to Docker Engine running directly on
Linux:

```bash
sudo sysctl -w vm.max_map_count=262144
```

**Three free ports on localhost:** 15173, 18000 and 18100. If any is taken, see
Knobs below to move them.

## Run it

There are two ways in, depending on how you got here.

**If you cloned this repository**, the images are pulled for you:

```bash
docker compose pull
docker compose up -d
```

**If you were handed `genesis-local.tar.gz`**, everything is inside it and
nothing is pulled:

```bash
tar xzf genesis-local.tar.gz
cd genesis-local
docker load -i images.tar
docker compose up -d
```

Either way the first start downloads the embedding model (about 130MB) from
Hugging Face, so the first run is never completely offline unless you also set
`EMBEDDING_PROVIDER=stub`, which costs you semantic search. The tarball route
also pulls s3mock and OpenSearch on first `up`, which keeps the download under
500MB rather than 1.2GB; ask for the offline bundle if you want those baked in.

First start also seeds the registry with the bundled corpus. Between the pulls,
the model and the seeding, expect several minutes before the UI answers. Then:

| | |
|---|---|
| Engine | http://localhost:15173 |
| Engine API | http://localhost:18000/docs |
| Registry API | http://localhost:18100/api/current/docs |

Stop with `docker compose down`. Add `-v` to also discard the registry's
storage and start from an empty bucket.

## The hackathon's own documents

The agenda and the welcome packet ship as cards, so the assistant answers the
questions people ask on the day -- where lunch is, which building they are in,
how to get an ALCF account, what the wifi is, where to go if the alarm sounds.
`docker compose up` loads them for you. They cannot go through the registry --
`seed_registry.py` only POSTs card types the registry has a subtype for, and
these have none -- so the seed service writes them to its storage directly and
the engine indexes them on startup. Ask the assistant "where is lunch?" as soon
as the stack is up.

They also show up in Explore under the **Hackathon Materials** filter. To
reload them after editing one, see `hackathon/README.md`.

## Writing a card

`skills/xcard-author/` is a Claude Code skill that writes an xCard and
registers it -- model, data, agent, resource or workflow. It starts from the
templates in `templates/`, which are valid cards tested against the registry,
fills them by asking and by reading the thing being described, checks the card
has actually been edited, and registers it.

Point Claude Code at this directory and ask it to describe your model, dataset
or agent as a card. Or use the templates directly: `templates/README.md` has
the loop.

## Knobs

Set these in the environment or a `.env` file next to `compose.yaml`.

| | |
|---|---|
| `UI_PORT`, `API_PORT`, `REGISTRY_PORT` | change ports on a clash |
| `SEED_LIMIT` | seed only the first N cards, for a faster start |
| `GENESIS_LOG_LEVEL` | `DEBUG` to see the sync in detail |
| `GENESIS_SEARCH_MIN_SCORE` | search relevance floor, default `0.55`; `0` returns everything ranked |
| `EMBEDDING_PROVIDER` | `stub` skips the model download, at the cost of semantic search |
| `GENESIS_AMSC_BASE_URL` | a different MAG deployment for everyone on this engine; a user can override it in Settings |
| `GENESIS_ARGO_BASE_URL`, `GENESIS_ALCF_BASE_URL` | where your own Argo or ALCF proxy listens, if not on the host |
| `OPENSEARCH_MEMORY_LOCK`, `OPENSEARCH_MEMLOCK_ULIMIT` | `false` and `67108864` on rootless Podman, which cannot lock memory |

## If something goes wrong

Start here, because it tells you which service to look at:

```bash
docker compose ps
```

Every service except `seed` should be running, and `opensearch` and `api` should
be healthy. `seed` is meant to exit; `Exited (0)` is success. Then read the logs
of whichever one is unhappy, for example `docker compose logs opensearch`.

| Symptom | Cause |
|---|---|
| Containers exit instantly, `exec format error` | A tarball built for the other architecture. See the first prerequisite. |
| `opensearch` exits during startup with no clear error | Not enough memory given to Docker. |
| `opensearch` logs `max virtual memory areas vm.max_map_count` | Native Linux Docker. Raise `vm.max_map_count`. |
| `opensearch` fails on memlock under Podman | Rootless Podman cannot lock memory. Set `OPENSEARCH_MEMORY_LOCK=false` and `OPENSEARCH_MEMLOCK_ULIMIT=67108864`. |
| Podman: `crun: controller 'pids' is not available` | A WSL 3.0.1 bug, not this stack. Set `cgroup_manager="cgroupfs"` in the machine's `/etc/containers/containers.conf`. |
| `unknown keyword` or similar from `docker compose` | Old `docker-compose` v1. Install Compose v2. |
| `port is already allocated` | Something else holds 15173, 18000 or 18100. Override it under Knobs. |
| `api` never becomes healthy, `ui` refuses to start | `ui` waits on `api` by design. The cause is in `docker compose logs api`. |
| Search returns far too much, or nothing semantic works | The embedding model did not download. Check `docker compose logs api` for the fetch. |
| The canvas assistant says no model is configured | Expected. Add a key under Settings then LLM Providers. |
| `CERTIFICATE_VERIFY_FAILED ... self-signed certificate in certificate chain` | Your network inspects TLS. See "Behind a TLS-inspecting proxy". |

## Behind a TLS-inspecting proxy

Some networks re-sign outbound HTTPS with a private CA. The containers do not
trust it, so the engine's first outbound call fails -- fetching the embedding
model:

```
fastembed ... Could not download model from HuggingFace:
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
self-signed certificate in certificate chain
```

It retries three times and gives up, and you get a stack without semantic
search.

Trust the CA rather than switching the check off. Export your proxy's root
certificate in PEM form, then bring the stack up with the overlay:

```bash
CA_BUNDLE=/path/to/corp-ca.crt \
  docker compose -f compose.yaml -f compose.ca.yaml up -d
```

Switching verification off does not work here, which is worth knowing before
you try it: `PYTHONHTTPSVERIFY` only affects Python's standard library, and
this download goes through huggingface_hub, which uses requests -- and
requests reads its own bundle and ignores that variable.

If you cannot get the certificate, `EMBEDDING_PROVIDER=stub` starts without
the model. Everything works except semantic search, which falls back to
matching on shared words.

The model is about 130MB and is cached in the `engine-data` volume, so this is
a once-per-machine problem rather than once per start.

## Register a card and find it

Registration goes to the registry, not the engine. The friendliest way is the
registry's own API docs:

**http://localhost:18100/api/current/docs**

Open `POST /api/current/registry/{xCard_type}`, click *Try it out*, pick the
type from the dropdown (`data_card`, `model_card`, `agent_card`,
`resource_card`), choose the matching content type, paste your card's Markdown
and Execute. You get back the id the registry assigned.

Or from a terminal. On Windows, write `curl.exe` rather than `curl`, because
PowerShell 5.1 aliases `curl` to `Invoke-WebRequest`, which does not understand
these flags. Put the command on one line too: PowerShell does not continue lines
with a trailing `\`.

```bash
curl -X POST http://localhost:18100/api/current/registry/agent_card \
  -H "Content-Type: text/vnd.genesis.agent-card+markdown" \
  --data-binary @my-agent-card.md
```

Then tell the engine to pick it up:

```bash
curl -X POST http://localhost:18000/api/v1/admin/resync
```

Search for it at http://localhost:15173 and it is there. The engine indexes
cards from registry storage, so a resync is what makes a newly registered card
searchable; without it you would have to restart the api container.

If the registry rejects your card, the error says which field failed. It
validates against the same xCard schema the engine does, so a card that passes
here passes on the cluster.

## What is in the stack

```
s3          stands in for AWS S3, holds the registry's objects
opensearch  the search index: BM25 over card text plus kNN vectors
registry    the real xCard Registry image
seed        pushes the bundled corpus in once, then exits
api         the Discovery Engine
ui          the web front end
```

Search matters more than it looks. Without OpenSearch the engine falls back to
an in-memory index that scores plain token overlap, so a two-word query matches
anything containing either word. With it you get the same hybrid search the
cluster runs: lexical matching combined with real embeddings, so
`agent that aligns samples at a light source` finds the right card even though
they share almost no words. Embeddings are local ONNX (bge-small); the model
downloads once, about 130MB, into the engine's data volume.

The registry has no filesystem backend; S3 is its only storage layer, so a
local S3-compatible service is required rather than optional. Its own test
suite uses MinIO, but MinIO no longer publishes pullable community images, so
this uses `adobe/s3mock`, which is smaller and purpose-built for this.

## How this differs from the cluster

Card content lives in the same place either way: the registry owns it.

On AmSC the engine discovers cards through the AmSC Data Catalog, which
enumerates what exists and hands back each card's registry URL. There is no
catalog locally, so the engine lists the storage bucket directly instead. That
is the `GENESIS_CARD_SOURCE=registry` path, and it is why registration and
search stay connected here without a catalog.

Authentication is absent on purpose. On the cluster Kong validates a PingAM
bearer before anything reaches the registry, and the registry declares the
scheme but does not validate it itself. With no gateway in front there is
nothing to authenticate against, so every port here binds to localhost only.
Do not expose them.

**The workflow canvas assistant is the one feature that needs a language
model.** Everything else works without one: search, the card graph, the
registry API and card registration.

Keys are **per user**, not per deployment. Nothing is configured in this compose
file. Open the engine, go to Settings then LLM Providers, pick your provider and
paste your own key. Each person brings whatever they already have.

The option that needs no personal Anthropic account is the **AmSC Model Access
Gateway (MAG)**. It speaks the Anthropic API directly and fronts Claude along
with many other models. You do need an AmSC account.

It may also need you to be on the AmSC network. The gateway sits behind
Cloudflare Access, and from an ordinary network we saw it refuse every request
with a 403 before the client was on the VPN. If the assistant reports a gateway
timeout and everything else in the engine works, check that first.

To get a token, from
[the MAG documentation](https://docs.amsc.energy.gov/mag-get-started/#3-create-a-mag-pat-personal-access-token):

1. Sign in to the MyAmSC dashboard at https://my.amsc.energy.gov/dashboard
2. Pick your AmSC project in the left navigation
3. Click **Personal Access Tokens**, then **Generate PAT**
4. Give it a description and submit, authorising Ping Identity if asked
5. Copy the token before closing the dialog. It is shown only once.

Then open the engine, go to Settings, LLM Providers, choose **AmSC** and paste
it. The token is a long string beginning `eyJ`. Nothing else needs configuring:
the engine already points at the endpoint the MAG documentation gives, and sends
the bearer token and model mappings that documentation specifies.

MAG has more than one deployment and they are not interchangeable: a token
minted against one does not work against another, and the failure is not
obvious -- the request hangs and the UI reports a gateway timeout. If your
token belongs elsewhere, set the endpoint in **Settings, LLM Providers**,
under the MAG key. `GENESIS_AMSC_BASE_URL` still sets it for a whole
deployment.

Two providers in the list, Argo and ALCF, expect a translating proxy running on
your own machine. This compose file points them at `host.docker.internal` so a
proxy on your host is reachable from the container; override
`GENESIS_ARGO_BASE_URL` or `GENESIS_ALCF_BASE_URL` if yours listens elsewhere.

Your key is stored encrypted in `/app/data/user_settings.db`, which is on the
`engine-data` volume, so it survives `docker compose down`. It does not survive
`docker compose down -v`.

If no key is configured the assistant now tells you so, rather than reporting a
generic failure.

## What the registry will not accept

Two of our card types have no registry subtype: `framework` and `workflow`.
The registry recognises exactly four, so those cards are skipped during seeding
and cannot be registered. Seeding reports what it skipped and why.

A handful of corpus cards also fail the registry's validation because they are
missing required fields. That is the same check the engine's own validator
applies, so the two agree about what is well formed.

## Rebuilding the images (maintainers)

```bash
deploy/local/build-bundle.sh
```

Builds the three images we own, fetches the registry source, and writes
`dist/genesis-local.tar.gz` carrying the images plus this README, the compose
file and the seed script. `OFFLINE=1` also bakes in s3mock and OpenSearch, so
the recipient needs no image registry. It does not make the stack fully
offline: the embedding model is still fetched on first start unless the
recipient sets `EMBEDDING_PROVIDER=stub`.

The bundle inherits the architecture of whatever machine builds it, and there
is no multi-architecture build yet, so a bundle built on Apple Silicon serves
only `arm64` recipients. Check before sending one out.

Building the registry image needs read access to `amsc2/modcon/dbs/data-cards`,
which its Dockerfile vendors one schema file from, so most people should use
the prebuilt bundle instead.
