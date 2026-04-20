# meshflow-rf-propagation

Container image for [meshtastic/meshtastic-site-planner](https://github.com/meshtastic/meshtastic-site-planner): a FastAPI service around SPLAT! for RF coverage prediction. This repository pins an upstream git revision, bakes optional UK terrain data for fast cold starts, and publishes the image to GitHub Container Registry (GHCR) for use by **meshflow-api** on an internal Docker network.

There is no application source code here beyond Docker glue and small upstream patches (Redis URL and optional baked SDF tiles).

## Quickstart (local)

1. Ensure Docker is installed.
2. From this repo root:

```bash
export UPSTREAM_REF="$(tr -d '[:space:]' < upstream-ref.txt)"
docker compose up --build
```

3. Open `http://localhost:8080/docs` (FastAPI OpenAPI). The API expects Redis; the Compose file runs a Redis sidecar and sets `REDIS_URL` accordingly.

## Consuming from meshflow-api

Pull the image from GHCR and attach it to the same Docker network as the API. Set:

- `REDIS_URL` — Redis instance reachable from the container (for example `redis://redis:6379/0` when a service is named `redis`).
- `SDF_DIR=/data/sdf` — pre-baked terrain tiles are included under this path in the published image.

Default env in the image includes `SDF_DIR=/data/sdf` and a placeholder `REDIS_URL`; override `REDIS_URL` in production.

## Image tags (GHCR)

| Tag | When |
|-----|------|
| `latest-dev` | Every push to `main` |
| `main-<sha7>` | Same build as `latest-dev` (Git short SHA of the repo commit) |
| `latest`, `<version>`, `<major>`, `<major>.<minor>` | GitHub Release published (semver tag) |

Images are `linux/amd64` only.

## Bumping upstream

The pinned upstream commit lives in **`upstream-ref.txt`** (full git SHA of `meshtastic/meshtastic-site-planner`).

1. Resolve the desired commit (for example `main` at a given time).
2. Update `upstream-ref.txt` with that SHA.
3. Branch, open a PR; CI rebuilds the image against the new ref.

CI reads `upstream-ref.txt` automatically; no workflow edits are required for a bump.

## Extending baked terrain (SRTM → SDF)

The image bakes a UK-wide set of SPLAT `.sdf` files under `/data/sdf` at build time. To cover a different region later, adjust the bake script (`docker/bake_uk_sdf.py`) or replace that step with a volume-backed lazy download strategy if image size becomes a problem.

## Weekly rebuild

A scheduled workflow rebuilds `latest-dev` so base-image security updates apply even when `upstream-ref.txt` is unchanged.
