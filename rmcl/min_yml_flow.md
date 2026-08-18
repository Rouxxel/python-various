# CI workflows guide (GitHub Actions)

**Purpose:** How to add, structure, and maintain `.github/workflows/*.yml` for automated checks and CI.  
**Companion:** [min_sec_prac.md](min_sec_prac.md) §8 covers security-specific pipeline steps (gitleaks, audits).

Copy this file into any project (repo root or `docs/`). Pair with workflow YAML under `.github/workflows/`.

| Document | Role |
| --- | --- |
| [min_sec_list.md](min_sec_list.md) | Security controls to verify |
| [min_sec_prac.md](min_sec_prac.md) | Security implementation + scripts |
| **This file** | CI structure, triggers, job patterns, YAML templates |

---

## What workflows should do

Every serious project should automate at least:

| Goal | Typical jobs |
| --- | --- |
| **Correctness** | Lint, format check, unit tests, compile/build |
| **Regression** | Integration tests, E2E (smoke) on PR |
| **Supply chain** | Dependency audit, secret scan, optional container/SBOM scan |
| **Deploy readiness** | Production build succeeds with CI env vars |

Workflows run on GitHub’s runners (`ubuntu-24.04` is a good default). They block bad merges when configured as required checks on `main`.

---

## Repository layout

```text
.github/
  workflows/
    ci.yml                 # single-package repo (simple)
    frontend.yml           # monorepo: path-filtered
    backend.yml
    security.yml           # optional: repo-wide security gates
  dependabot.yml           # optional: dependency update PRs
  pull_request_template.md # optional
```

**Rule of thumb**

- **One repo, one app** → one `ci.yml` is enough.
- **Monorepo** → one workflow per deployable unit, with `paths:` filters so unrelated changes don’t run everything.

---

## Core YAML concepts

```yaml
name: CI                    # Display name in GitHub UI

on:                         # When to run
  pull_request:
  push:
    branches: [main]

permissions:                # Least privilege (see below)
  contents: read

concurrency:                # Optional: cancel outdated runs on same PR
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:                  # Job id (parallel with other jobs)
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: . # or subdirectory for monorepos
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

| Piece | Meaning |
| --- | --- |
| `on` | Triggers: `push`, `pull_request`, `schedule`, `workflow_dispatch` |
| `paths` / `paths-ignore` | Only run when certain files change |
| `jobs` | Parallel units; failure fails the workflow unless `continue-on-error` |
| `needs` | Run job B only after job A succeeds |
| `services` | Sidecar containers (Postgres, Redis) for integration tests |
| `env` | Environment variables for steps |
| `secrets` | Encrypted repo/org secrets — never log them |

---

## Triggers — common practice

### Pull requests (required)

Run on every PR to catch issues before merge.

```yaml
on:
  pull_request:
```

### Push to main (recommended)

Catch issues on direct pushes and keep `main` green.

```yaml
on:
  push:
    branches: [main]
```

### Path filters (monorepos)

Only run frontend CI when frontend files change:

```yaml
on:
  pull_request:
    paths:
      - "frontend/**"
      - ".github/workflows/frontend.yml"
  push:
    branches: [main]
    paths:
      - "frontend/**"
      - ".github/workflows/frontend.yml"
```

Always include the workflow file itself in `paths` so workflow edits are validated.

### Manual runs

Useful for debugging CI or on-demand security scans:

```yaml
on:
  workflow_dispatch:
```

---

## Permissions (least privilege)

Default to read-only unless the workflow must write (releases, comments, deployments):

```yaml
permissions:
  contents: read
```

| Workflow type | Typical permissions |
| --- | --- |
| Lint / test / build | `contents: read` |
| PR comment bot | `pull-requests: write` |
| Publish package / deploy | `contents: write`, `id-token: write` (OIDC) |
| Security scan upload | `security-events: write` (SARIF) |

Avoid `permissions: write-all`.

---

## Job patterns

Split CI into **focused jobs** so failures are clear and jobs can run in parallel:

```text
quality        → lint, format, test, build
supply-chain   → audit, secret patterns, optional image scan
e2e            → Playwright/Cypress (optional, slower)
integration    → DB migrations, API tests with services
```

Use `needs: [quality]` on slower jobs if you want fast feedback first (optional).

---

## Template: minimal Node / Bun / npm frontend

Adjust `working-directory`, install command, and scripts to match your package manager.

```yaml
name: Frontend

on:
  pull_request:
    paths:
      - "frontend/**"
      - ".github/workflows/frontend.yml"
  push:
    branches: [main]
    paths:
      - "frontend/**"
      - ".github/workflows/frontend.yml"

permissions:
  contents: read

defaults:
  run:
    working-directory: frontend

jobs:
  quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm

      - name: Install
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Verify formatting
        run: npm run format:check

      - name: Test
        run: npm test

      - name: Production build
        run: npm run build
        env:
          # Use dummy/public values — never real production secrets
          API_BASE_URL: https://api.example.test

  supply-chain:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - run: npm ci
      - name: Audit dependencies
        run: npm audit --audit-level=high
        continue-on-error: true   # set false before treating as gate

      - name: Block committed env files and obvious secrets
        run: |
          test ! -f .env
          ! grep -RInE '(PRIVATE KEY-----|postgresql://|api[_-]?key\s*=\s*["'\''][^"'\'']+["'\''])' \
            --include='*.ts' --include='*.tsx' --include='*.js' \
            --exclude='*.test.*' . || \
            (echo "Forbidden secret pattern in sources." && exit 1)
```

**Bun:** replace `setup-node` + `npm ci` with `oven-sh/setup-bun@v2` and `bun install --frozen-lockfile`.

---

## Template: .NET backend

```yaml
name: Backend

on:
  pull_request:
    paths:
      - "backend/**"
      - ".github/workflows/backend.yml"
  push:
    branches: [main]
    paths:
      - "backend/**"
      - ".github/workflows/backend.yml"

permissions:
  contents: read

defaults:
  run:
    working-directory: backend

jobs:
  quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Verify formatting
        run: dotnet format --verify-no-changes

      - run: dotnet build --configuration Release
      - run: dotnet test --configuration Release --no-build

  supply-chain:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
      - run: dotnet restore
      - name: Vulnerable packages
        run: dotnet list package --vulnerable --include-transitive

      # Optional: build and scan container
      - name: Build image
        working-directory: ${{ github.workspace }}
        run: docker build -f backend/Dockerfile -t app-backend:ci .
      - name: Scan image
        uses: aquasecurity/trivy-action@v0.36.0
        with:
          image-ref: app-backend:ci
          severity: CRITICAL,HIGH
          exit-code: "1"
          ignore-unfixed: true
          scanners: vuln
```

Point `dotnet format` and solution path at your `.sln` or project file.

---

## Template: Rust

```yaml
name: Rust

on:
  pull_request:
    paths:
      - "crates/**"
      - "Cargo.toml"
      - "Cargo.lock"
      - "rust-toolchain.toml"
      - ".github/workflows/rust.yml"
  push:
    branches: [main]
    paths:
      - "crates/**"
      - "Cargo.toml"
      - "Cargo.lock"
      - "rust-toolchain.toml"
      - ".github/workflows/rust.yml"

permissions:
  contents: read

defaults:
  run:
    working-directory: .

jobs:
  quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo fmt --all -- --check
      - run: cargo clippy --workspace --all-targets -- -D warnings
      - run: cargo test --workspace

  supply-chain:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - uses: EmbarkStudios/cargo-deny-action@v2
        with:
          command: check advisories bans licenses sources
      - uses: rustsec/audit-check@v2
```

---

## Template: integration tests with Postgres

```yaml
  integration:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: app_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Apply migrations
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/app_test
        run: ./scripts/migrate.sh
      - name: Integration tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/app_test
        run: npm run test:integration
```

Use ephemeral CI credentials only — never production DB URLs in YAML.

---

## Template: E2E (Playwright)

Keep E2E separate — it’s slower and flakier than unit tests.

```yaml
  e2e:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - run: npm ci
      - run: npx playwright install chromium --with-deps
      - run: npm run test:e2e
        env:
          CI: "true"
          # Mock external APIs in CI when possible
          E2E_MOCK: "1"
          API_BASE_URL: https://api.example.test
```

---

## Template: repo-wide security workflow

Runs on all PRs regardless of paths (or on `schedule` weekly):

```yaml
name: Security

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"   # weekly Monday 06:00 UTC

permissions:
  contents: read
  security-events: write

jobs:
  secrets:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2

  dependency-review:
    runs-on: ubuntu-24.04
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
```

Enable **Dependency graph** and **Dependabot** in repo Settings → Security.

---

## Template: single-package repo (`ci.yml`)

For a simple app with everything at repo root:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

Replace setup steps for Python, Go, etc. using the matching `setup-*` action.

---

## Environment variables and secrets in CI

| Use | Where | Example |
| --- | --- | --- |
| Dummy public config | `env:` in workflow | `API_URL: https://api.example.test` |
| Test tokens (scoped, rotatable) | GitHub **Secrets** | `settings → Secrets → Actions` |
| Never | Hardcoded in YAML | production DB password, `service_role` keys |

```yaml
      - name: Deploy staging
        env:
          DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}
        run: ./deploy.sh
```

**Fork PRs:** secrets are not passed to workflows from fork PRs by default (security feature).

---

## Caching (speed)

| Stack | Action |
| --- | --- |
| Node | `cache: npm` / `cache: yarn` in `setup-node` |
| .NET | `actions/setup-dotnet` caches NuGet automatically |
| Rust | `Swatinem/rust-cache@v2` |
| Docker | layer cache via `docker/build-push-action` |

Pin action versions (`@v4`) — avoid `@main`.

---

## Required checks on `main`

After workflows exist:

1. GitHub → **Settings → Branches → Branch protection rules**
2. Require status checks before merge (e.g. `Frontend / quality`, `Backend / quality`)
3. Require PR reviews (optional but recommended)

Without required checks, workflows are informative but don’t block merges.

---

## Dependabot (optional `dependabot.yml`)

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule:
      interval: weekly
    open-pull-requests-limit: 10

  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

Also enable **npm**, **NuGet**, **Docker**, **pip** as needed per ecosystem.

---

## Standard checks checklist

Use when adding CI to a new project:

### Every project

- [ ] Workflow runs on `pull_request`
- [ ] Workflow runs on `push` to `main`
- [ ] `permissions: contents: read` (or tighter scoped writes)
- [ ] Install uses lockfile (`npm ci`, `--frozen-lockfile`, `dotnet restore`)
- [ ] Lint + test + build in CI
- [ ] No real secrets in YAML or committed `.env`
- [ ] Branch protection requires CI pass

### Frontend

- [ ] Lint + format check
- [ ] Unit tests
- [ ] Production build with CI env vars
- [ ] `npm audit` / `bun audit` (supply-chain job)
- [ ] E2E smoke (optional, separate job)

### Backend API

- [ ] Format verify + build + unit tests
- [ ] Vulnerable package scan
- [ ] Integration tests with service containers (DB, Redis)
- [ ] Migration apply smoke test (if applicable)
- [ ] Container build + Trivy scan (if Dockerized)

### Rust / native

- [ ] `fmt`, `clippy`, `test`
- [ ] `cargo audit` / `cargo-deny`

### Security (repo-wide)

- [ ] gitleaks or GitHub secret scanning
- [ ] Dependency review on PRs
- [ ] Dependabot or Renovate enabled

### Monorepo

- [ ] Path filters per app/service
- [ ] Workflow file included in its own `paths`
- [ ] Separate jobs per deployable unit

---

## Common mistakes

| Mistake | Fix |
| --- | --- |
| CI only on push, not PR | Add `pull_request` trigger |
| No path filters in huge monorepo | Add `paths:` per workflow |
| `npm install` without lockfile | Use `npm ci` / frozen lockfile |
| Secrets in workflow YAML | GitHub Secrets + OIDC |
| One giant 30-minute job | Split quality / supply-chain / e2e |
| `continue-on-error: true` forever | Tighten before production gate |
| Production API keys in E2E | Mock externals; use `example.test` URLs |
| `@main` on actions | Pin major version tags |
| No branch protection | Required checks don’t block bad merges |

---

## Map to security docs

| Security checklist item | CI workflow |
| --- | --- |
| Dependency patching | `npm audit`, `dotnet list package --vulnerable`, Dependabot |
| Secrets not in Git | gitleaks job, grep patterns, no `.env` in repo |
| Security regression tests | `test-auth-boundary`, Playwright smoke |
| Container hardening | Docker build + Trivy in supply-chain job |
| SAST | CodeQL workflow (optional GitHub template) |

See [min_sec_prac.md](min_sec_prac.md) §8 for a minimal security-only Actions snippet.

---

## Adding CI to a project with no workflows yet

1. Create `.github/workflows/ci.yml` from the single-package template (or stack-specific template).
2. Ensure `lint`, `test`, and `build` scripts exist locally and pass.
3. Push branch → open PR → fix red CI.
4. Add `security.yml` with gitleaks.
5. Enable branch protection + required checks.
6. Add `dependabot.yml` if desired.
7. For monorepos, split workflows and add `paths` filters.

---

*General reference — copy into any project. Last updated: 2026-08-18*
