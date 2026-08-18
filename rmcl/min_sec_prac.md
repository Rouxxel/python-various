# Security practices, patterns & scripts

**Purpose:** How to implement the controls in [min_sec_list.md](min_sec_list.md).

| Document | Role |
| --- | --- |
| `min_sec_list.md` | **What to verify** — checkbox reminders before ship |
| **This file** | **How to do it** — patterns, tooling, runnable scripts |

Copy both files (and optionally the `security-scripts/` folder) into any project. The checklist names outcomes (“short-lived tokens”, “RLS enabled”) but does not spell out implementation. This guide fills that gap.

---

## Runnable scripts (optional)

If you copied the `security-scripts/` folder next to this file:

| Script | Purpose |
| --- | --- |
| `security-scripts/check-security-headers.ps1` | Verify HSTS, CSP, frame denial, etc. on a live URL |
| `security-scripts/audit-dependencies.ps1` | `npm audit` + `dotnet list package --vulnerable` |
| `security-scripts/test-auth-boundary.ps1` | Confirm a route returns 401/403 without a token |

```powershell
.\security-scripts\check-security-headers.ps1 https://your-app.example.com
.\security-scripts\audit-dependencies.ps1
.\security-scripts\test-auth-boundary.ps1 -BaseUrl https://api.example.com -ProtectedPath /api/v1/me
```

On macOS/Linux, adapt the PowerShell scripts or use the equivalent `curl` / shell snippets in the sections below.

---

## 1. Authentication & API boundaries

### Pattern: public vs protected routes

Only explicit auth endpoints are anonymous. Everything else validates a token **on the server** (or via RLS for direct DB access).

```
Public (no session required):
  POST /auth/signup
  POST /auth/login
  POST /auth/forgot-password   (if applicable)

Protected (session/JWT required):
  All other /api/* routes
```

**Express (Node) middleware sketch:**

```javascript
const publicPaths = new Set(["/auth/login", "/auth/signup"]);

app.use((req, res, next) => {
  if (publicPaths.has(req.path)) return next();
  const token = req.headers.authorization?.replace(/^Bearer\s+/i, "");
  if (!token) return res.status(401).json({ error: "unauthorized" });
  try {
    req.user = verifyJwt(token); // library validates sig, exp, iss, aud
    next();
  } catch {
    return res.status(401).json({ error: "unauthorized" });
  }
});
```

**ASP.NET Core sketch:**

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.Authority = configuration["Auth:Authority"];
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }
        };
    });

app.MapControllers().RequireAuthorization();
```

### Pattern: managed auth + direct DB access (e.g. Supabase, Firebase)

1. **Client** — attach `Authorization: Bearer <access_token>` to API calls (or use the vendor client so RLS applies automatically).
2. **Server / Edge Function** — verify JWT with the provider’s JWKS or user-validation API.
3. **Database** — **row-level security on every table**; policies scoped to the authenticated user id.

```sql
-- Example: users only read their own rows
alter table messages enable row level security;

create policy "messages_select_own"
  on messages for select
  using (auth.uid() = user_id);

create policy "messages_insert_own"
  on messages for insert
  with check (auth.uid() = user_id);
```

4. **Never** expose admin/service keys in the frontend.

### Pattern: short-lived access + refresh rotation (standard)

| Setting | Typical value | Notes |
| --- | --- | --- |
| Access token TTL | 5–15 minutes | Configure in your auth provider dashboard |
| Refresh token | Rotate on each use | Invalidates stolen refresh after next legitimate refresh |
| Logout | Revoke session server-side | Provider sign-out / revoke-all-sessions API |

Checklist item: *“Short-lived access tokens; refresh rotation; revoke on logout”* → configure in auth provider + call sign-out/revoke APIs.

### Pattern: aggressive token rotation (optional hardening)

Optional when a stolen **access** token must die quickly:

- App refreshes session on an interval (e.g. 1–5 minutes).
- Server rejects access tokens past a short TTL **or** tracks a session version server-side.

**Tradeoffs:** multi-tab races, flaky networks, useless if refresh token is stolen. Pair with row-level security and XSS prevention.

```typescript
// Client watchdog — coordinate with your auth SDK to avoid double-refresh races
import { createClient } from "@supabase/supabase-js";

const authClient = createClient(AUTH_URL, PUBLIC_ANON_KEY);

setInterval(async () => {
  const { error } = await authClient.auth.refreshSession();
  if (error) {
    await authClient.auth.signOut();
  }
}, 5 * 60 * 1000); // 5 min is saner than 1 min for most apps
```

### Pattern: authorization (not just authentication)

After auth, check **resource ownership**:

```javascript
const row = await db.message.findUnique({ where: { id: req.params.id } });
if (!row || row.userId !== req.user.id) return res.status(404).end(); // or 403
```

Test with two users and swapped IDs (IDOR regression test).

---

## 2. Rate limiting & abuse

### Application-level (single instance)

**Node — `express-rate-limit`:**

```javascript
import rateLimit from "express-rate-limit";

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use("/auth/login", authLimiter);
```

**ASP.NET — middleware attribute** (concept): per-endpoint limits keyed by client IP.

### Distributed (multiple instances)

Use Redis-backed limiter or **API gateway** rules (Cloudflare, AWS WAF, Kong, nginx `limit_req`).

### Smoke test with curl

```bash
# Expect 429 after threshold
for i in $(seq 1 30); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST https://api.example.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done
```

---

## 3. Transport & security headers

### Minimum header set

| Header | Example value |
| --- | --- |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` or CSP | `DENY` or `frame-ancestors 'none'` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` or `no-referrer` |
| `Content-Security-Policy` | Start strict; loosen only as needed |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |

### nginx snippet

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'none'" always;
```

### Verify live site

```bash
curl -sI https://your-app.example.com | grep -iE 'strict-transport|content-security|x-frame|x-content-type|referrer-policy'
```

Or run `security-scripts/check-security-headers.ps1` if you copied that folder.

---

## 4. Input validation & injection prevention

### API boundary — schema validation

**Zod (TypeScript):**

```typescript
import { z } from "zod";

const CreateMessage = z.object({
  text: z.string().min(1).max(2000),
});
const body = CreateMessage.parse(req.body); // throws → map to 400
```

**ASP.NET** — data annotations + `FluentValidation` or minimal APIs `AddEndpointFilter`.

### SQL

- Always parameterized queries / ORM.
- DB user: `SELECT`, `INSERT`, `UPDATE`, `DELETE` only — no `DDL` at runtime.

### File uploads

```javascript
const ALLOWED = new Set(["image/jpeg", "image/png", "application/pdf"]);
const MAX_BYTES = 10 * 1024 * 1024;

if (!ALLOWED.has(file.mimetype)) throw forbidden();
if (file.size > MAX_BYTES) throw payloadTooLarge();
// Also verify magic bytes server-side; store outside web root
```

---

## 5. Sessions, cookies & CSRF

### Secure cookie flags (session-based auth)

```
Set-Cookie: session=...; Path=/; HttpOnly; Secure; SameSite=Strict
```

### CSRF (cookie sessions)

- `SameSite=Strict` on session cookie.
- Double-submit or synchronizer token on state-changing requests.
- Verify `Origin` / `Referer` on POST/PUT/DELETE.

### Bearer tokens (SPA + API)

CSRF risk is lower (no automatic cookie send). Still need XSS protection — tokens in memory beat `localStorage` when possible.

---

## 6. Secrets & configuration

### Environment template (never commit real values)

```bash
# .env.example — commit this
DATABASE_URL=
JWT_SECRET=
AUTH_PROVIDER_URL=
AUTH_PUBLIC_KEY=
# Admin/service keys ONLY on server — never in frontend bundles
AUTH_SERVICE_KEY=
```

### Scan repo for leaked secrets

```bash
# gitleaks (install once: https://github.com/gitleaks/gitleaks)
gitleaks detect --source . --verbose

# npm alternative
npx trufflehog filesystem . --only-verified
```

### Pre-commit hook (optional)

```yaml
# .pre-commit-config.yaml snippet
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

---

## 7. Logging & errors

### Safe logging

```javascript
logger.info("login_failed", { userId: user?.id, ip: req.ip }); // no password, no token
```

### Safe client errors

```json
{ "error": "invalid_credentials", "detail": "Authentication failed." }
```

Never return stack traces, connection strings, or internal paths to clients in production.

### Sensitive API responses

```
Cache-Control: no-store
Pragma: no-cache
```

---

## 8. CI/CD security gates

### GitHub Actions — minimal pipeline

```yaml
name: security

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Secret scan
        uses: gitleaks/gitleaks-action@v2

      - name: npm audit
        if: hashFiles('package.json') != ''
        run: npm audit --audit-level=high
        continue-on-error: true  # tighten to false before prod

      - name: dotnet vulnerable packages
        if: hashFiles('**/*.sln') != ''
        run: dotnet list package --vulnerable --include-transitive
        continue-on-error: true
```

### Dependabot / Renovate

Enable in GitHub: **Settings → Security → Dependabot alerts** + version updates for npm, NuGet, Docker, etc.

---

## 9. Container & deploy hardening

```yaml
# docker-compose / K8s concepts
security_opt:
  - no-new-privileges:true
read_only: true
user: "1000:1000"
deploy:
  resources:
    limits:
      cpus: "1"
      memory: 512M
```

- Non-root user
- Read-only root filesystem + tmp mount
- Internal services not published on public ports
- TLS terminated at gateway; origin firewall allows gateway only

---

## 10. Testing checklist (automated smoke)

| Test | Command / approach |
| --- | --- |
| Anonymous blocked | `test-auth-boundary.ps1` or curl without token → 401/403 |
| Headers present | `check-security-headers.ps1` or `curl -sI` |
| IDOR | Integration test: user A token → user B resource → 403/404 |
| Rate limit | Burst script → expect `429` |
| JWT expired | Token with past `exp` → `401` |
| Row-level security | Client/anon key cannot read other users’ rows |

**Playwright / API test sketch:**

```typescript
test("protected route rejects anonymous", async ({ request }) => {
  const res = await request.get("/api/v1/me");
  expect(res.status()).toBe(401);
});
```

---

## 11. Tooling reference

| Category | Tools |
| --- | --- |
| Secret scanning | gitleaks, trufflehog, GitHub secret scanning |
| Dependency audit | npm audit, `dotnet list package --vulnerable`, pip-audit, cargo audit |
| SAST | CodeQL, Semgrep, SonarQube |
| DAST | OWASP ZAP (staging only) |
| Headers / TLS | securityheaders.com, `curl -sI`, testssl.sh |
| Auth / JWT | jwt.io (debug only — never paste prod tokens) |
| Managed auth + RLS | Provider auth settings, RLS policies, leaked-password protection |

---

## 12. Map checklist items → this guide

| Checklist section | See here |
| --- | --- |
| Every non-public route requires authentication | §1 middleware patterns |
| JWT validated | §1 server-side verify |
| Short-lived tokens; refresh rotation | §1 rotation patterns |
| Row-level security (direct DB clients) | §1 SQL policies |
| Rate limits | §2 |
| Security headers | §3 + header check script |
| Input validation | §4 |
| Cookies / CSRF | §5 |
| Secrets not in Git | §6 |
| Safe logging / errors | §7 |
| CI gates | §8 |
| Container hardening | §9 |
| Automated smoke tests | §10 |

---

*General reference — copy into any project. Last updated: 2026-08-18*
