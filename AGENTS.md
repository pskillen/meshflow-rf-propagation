# meshflow-rf-propagation – Agent Context

Thin Docker wrapper around [meshtastic/meshtastic-site-planner](https://github.com/meshtastic/meshtastic-site-planner) (FastAPI + SPLAT!). **meshflow-api** pulls the published image from GHCR; there is no Python application maintained in this repo beyond Docker scripts and tiny upstream patches.

## Key files

| File | Role |
|------|------|
| `upstream-ref.txt` | Full git SHA of upstream `meshtastic-site-planner` to clone at image build time |
| `Dockerfile` | Multi-stage build: clone upstream, patch, compile SPLAT!, bake UK SDF tiles, runtime image |
| `docker-compose.yaml` | Local dev: app + Redis |
| `.github/workflows/docker-build.yaml` | Reusable build and push to GHCR |
| `.github/workflows/main.yaml` | Push to `main` → `latest-dev` + `main-<sha7>` |
| `.github/workflows/release.yaml` | Release published → semver tags |
| `.github/workflows/weekly-refresh.yaml` | Cron rebuild of `latest-dev` |
| `.github/workflows/pull-request.yaml` | Lint + image build + boot smoke (`/docs`) |

## Bump upstream

Edit `upstream-ref.txt` with the target upstream commit SHA, branch, PR. CI passes `UPSTREAM_REF` from that file into `docker build`.

## Local testing

```bash
export UPSTREAM_REF="$(tr -d '[:space:]' < upstream-ref.txt)"
docker compose up --build
```

Then hit `http://localhost:8080/docs`. Redis must be reachable at `REDIS_URL`.

## Source control

Follow `.cursor/skills/meshflow-git-workflow/SKILL.md` (conventional commits, branch naming when using issues). For PR descriptions, follow `.github/pull_request_template.md` and write `tmp/PR.md` when asked.

Use the **github-personal** MCP for GitHub operations. The `gh` CLI is not available; do not use it.

## Plan mode

When planning work: branch from latest `origin/main`, implement, commit, push, open a PR via the github-personal MCP.
