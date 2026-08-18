# Web & API security checklist

A general reminder checklist for new projects. Use it during design, before launch, and when adding features.

**Rule:** UI restrictions, hidden URLs, and CORS are not authentication. The API is the real boundary.

Copy this file into any project (e.g. repo root or `docs/security/`). Pair with [min_sec_list.md](min_sec_list.md) for implementation patterns and scripts.

**This checklist is mostly “what to verify,” not step-by-step implementation.** Each line implies a solution (e.g. “short-lived access tokens” → configure TTL + refresh rotation in `min_sec_list.md`), but details live in the practices guide.

---

## Before you build — design questions

- [ ] Who can call each endpoint (public, user, admin, internal service)?
- [ ] What proves identity (password, OAuth, JWT, mTLS)?
- [ ] What data is sensitive, temporary, or never stored?
- [ ] What happens if the server or database is compromised (minimize blast radius)?
- [ ] Is the browser calling the API directly (SPA) or through a backend-for-frontend (BFF)?
- [ ] What are the expensive operations (email, OCR, payments, crypto) and who can trigger them?
- [ ] Threat model documented (even a short STRIDE or abuse-case list)?

---

## Part 1 — Basic (foundational)

### Authentication & access control

- [ ] Every non-public route requires authentication
- [ ] Authorization checked per request (role + resource / object-level)
- [ ] Deny by default; explicit allow policies
- [ ] No spoofable auth (signed JWT, session, or mTLS — not client-supplied role headers)
- [ ] JWT validated: signature, `exp`, `iss`, `aud`, allowed algorithms only
- [ ] Admin / debug / Swagger disabled or network-restricted in production
- [ ] Least privilege roles; separate end-user vs staff vs admin capabilities
- [ ] IDOR tested: user A cannot access user B’s resources by changing IDs
- [ ] Opaque or UUID resource IDs where enumeration is a risk

### Accounts & verification

- [ ] Signup requires verification appropriate to risk (email, SMS, CAPTCHA, identity check)
- [ ] Login/register errors do not reveal whether an account exists
- [ ] MFA for high-value accounts (admin, billing, sensitive data)
- [ ] Account lockout or backoff after repeated failures
- [ ] No default credentials in production
- [ ] Password policy + breached-password check (if using passwords)

### Abuse, rate limits & availability

- [ ] Server-side rate limits on auth, signup, search, and write endpoints
- [ ] Rate limits at API gateway / WAF (not only in app code)
- [ ] Distributed rate limiting if you run multiple instances (Redis, gateway)
- [ ] `429` responses with sane retry guidance
- [ ] Expensive work requires auth and quotas before processing
- [ ] Request body size limits and request timeouts
- [ ] Connection limits and CDN/gateway protection for obvious DoS patterns

### Transport & browser security

- [ ] TLS everywhere in production (prefer TLS 1.3)
- [ ] HTTP redirects to HTTPS; HSTS in production
- [ ] Security headers: CSP, `X-Content-Type-Options`, frame denial, `Referrer-Policy`, `Permissions-Policy`
- [ ] CORS: strict origin allow-list; never `*` with credentials
- [ ] Understand CORS protects browsers only — not Postman/curl
- [ ] Clickjacking mitigated (`frame-ancestors` or `X-Frame-Options`)

### Input validation & injection

- [ ] All inputs validated (schema, type, length, format) on the server
- [ ] SQL: parameterized queries / ORM; no string-concatenated SQL
- [ ] XSS: output encoding; CSP; avoid rendering raw HTML from users
- [ ] CSRF: SameSite cookies + tokens if using cookie-based sessions
- [ ] No shell commands with user input
- [ ] Path traversal prevented; uploads jailed to a dedicated directory
- [ ] File uploads: size limits, MIME + magic-byte check, malware scan if applicable
- [ ] Mass assignment prevented (explicit DTOs; ignore unknown JSON fields)
- [ ] SSRF: no fetching arbitrary user-supplied URLs without allow-list

### Data protection & logging

- [ ] Data classified (public, internal, sensitive, secret)
- [ ] Retention policy defined; temp data deleted after use
- [ ] Passwords hashed with modern algorithm (Argon2, bcrypt) — never plaintext
- [ ] Secrets not in Git (scan repos; use env / vault)
- [ ] Logs never contain passwords, tokens, full PII, or private keys
- [ ] Error responses generic for clients; details logged server-side only
- [ ] Sensitive responses use `Cache-Control: no-store`
- [ ] Backups encrypted; retention aligned with privacy policy

### Sessions & cookies

- [ ] Cookies: `Secure`, `HttpOnly`, `SameSite=Strict` (or `Lax` where needed)
- [ ] Session ID regenerated on login (fixation prevention)
- [ ] Short-lived access tokens; refresh rotation; revoke on logout
- [ ] Tokens not in URLs or query strings

### Configuration & deployment

- [ ] Production config separate from dev; debug off in prod
- [ ] Dev/staging stacks not exposed to the internet with prod data
- [ ] Dependencies patched; Dependabot or equivalent enabled
- [ ] Cloud IAM least privilege; scoped API keys per service
- [ ] Startup validation fails if required secrets or security settings missing
- [ ] Container/process runs non-root where possible

---

## Part 2 — Advanced

### Tokens, services & replay

- [ ] Refresh tokens stored and rotated securely
- [ ] Replay protection for sensitive operations (nonce, idempotency key, one-time tokens)
- [ ] Idempotency keys scoped to authenticated principal
- [ ] Service-to-service: mTLS or signed service tokens (not IP trust alone)
- [ ] Internal services on private networks; not on public edge

### Application logic & architecture

- [ ] Multi-step workflows enforced server-side (state machine, not UI-only steps)
- [ ] Race conditions handled (DB unique constraints, transactions, locks)
- [ ] Untrusted client input never treated as verified truth
- [ ] BFF vs SPA architecture documented; auth model matches reality
- [ ] Business-logic abuse cases tested (skip payment, double redeem, etc.)

### Deserialization & parsers

- [ ] No deserializing untrusted objects to arbitrary types
- [ ] JSON/schema validation at API boundary
- [ ] XML parsers safe (no XXE) if XML is used

### Cryptography

- [ ] Modern algorithms only (no MD5/SHA1 for security; TLS 1.3; AES-GCM, Ed25519, etc.)
- [ ] Keys in vault/HSM; separate keys per environment
- [ ] Key rotation plan documented
- [ ] Constant-time comparison for secrets where applicable

### Infrastructure & supply chain

- [ ] Dependency pinning; SBOM or audit trail
- [ ] Container images minimal; non-root; read-only root FS where possible
- [ ] No secrets baked into image layers
- [ ] Origin not directly reachable (firewall to gateway only)
- [ ] DNS/subdomain inventory; no dangling records (subdomain takeover)
- [ ] WAF or bot protection for public APIs at scale

### Database & multi-tenant

- [ ] Row Level Security (RLS) if clients can query DB directly (e.g. Supabase, Firebase)
- [ ] App DB user cannot DROP/ALTER schema at runtime
- [ ] Migrations use separate elevated credentials
- [ ] Tenant isolation verified in tests

### Observability & operations

- [ ] Structured logging; log input sanitized (log injection)
- [ ] Metrics use low-cardinality labels (no user IDs in labels)
- [ ] Incident runbook: breach, credential leak, DDoS, dependency CVE
- [ ] Security regression tests in CI (auth, IDOR, rate limit smoke tests)
- [ ] Alerting on auth failures, rate-limit spikes, error rate anomalies

### Advanced web/API attacks

- [ ] Prototype pollution mitigated in JS (schema validation, safe merge)
- [ ] Cache poisoning: correct `Vary` / no cache on authenticated routes
- [ ] Host header attacks: fixed allowed hosts behind proxies
- [ ] GraphQL: query depth/cost limits if used
- [ ] WebSockets: same auth model as HTTP

### People & process

- [ ] Insider access minimized; audit sensitive operations
- [ ] Support/social-engineering procedures (no “reset password” without verification)
- [ ] Security review before major releases
- [ ] Responsible disclosure / security contact published

---

## Every new endpoint — 60-second check

- [ ] Auth required?
- [ ] AuthZ for this specific resource?
- [ ] Rate limited?
- [ ] Input validated (type, size, schema)?
- [ ] Safe errors (no stack traces)?
- [ ] Nothing sensitive logged?
- [ ] TLS in production?
- [ ] Test: unauthenticated, wrong user, abuse burst?

---

## Never rely on these alone

| If you only do this… | Attacker can still… |
| --- | --- |
| Hide the API URL | Find it in JS, docs, mobile app, traffic |
| CORS allow-list | Call API with curl/Postman |
| Check `Origin` / `Referer` on server | Spoof headers outside browsers |
| Client-side validation | Send raw HTTP requests |
| Allowlist “frontend server IP” | SPA traffic comes from user devices, not one IP |
| CAPTCHA only on the form | Hit the API directly |

---

## Launch gate (minimum before production)

- [ ] TLS + HSTS live
- [ ] Auth and authZ on all sensitive routes
- [ ] Rate limits (app + edge)
- [ ] Secrets out of source control
- [ ] Prod debug/admin tooling off or locked down
- [ ] Security headers configured
- [ ] Error handling does not leak internals
- [ ] Dependency audit clean or accepted risks documented
- [ ] Backup and restore tested
- [ ] Someone knows the incident playbook

---

## Suggested review cadence

| When | Do |
| --- | --- |
| New feature | “Every new endpoint” checklist |
| Pre-launch | Launch gate + Part 1 full pass |
| Quarterly | Part 2 spot-check + dependency/CVE review |
| After incident | Update checklist and runbooks |

---

*General reference — copy or adapt for any project. Last updated: 2026-08-18*
