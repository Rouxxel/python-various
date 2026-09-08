# Security Conventions

This document describes the security logic conventions used on a project by me (Rouxxel, Sebastian Russo) **simple-chat-backend**, so the same patterns can be reused in future projects that require a deployed backend, whether locally or on the cloud. It is derived from the middleware stack, every router under `src/routers/`, input validators/sanitizers, and the Supabase RLS/migrations under `supabase/`.

**Goal:** Even if an attacker discovers the backend URL and all route paths, they should not be able to act as another user, call expensive third-party APIs without a real session, or read/write another user’s data.

---

## 1. Defense in depth (layers)

Security is intentionally stacked. A request must pass **multiple** independent checks:

| Layer | Where | What it does |
|-------|--------|----------------|
| 1. Network / app config | `main.py` | CORS allowlist (no `*`), docs off by default, secrets from env |
| 2. Middleware | `src/middleware/` | Body size limit → JWT Bearer verification → security headers |
| 3. Handler validation | `src/utils/validators.py`, routers | Format checks (JWT shape, UUID, email, password, chat payload) |
| 4. Handler identity binding | Most protected routers | `auth.get_user(access_token)` then `user.id == user_id` (or email match) |
| 5. Client scoped to JWT | `supabase.postgrest.auth(access_token)` | DB calls run as the authenticated role, not service role |
| 6. Database RLS | `supabase/migrations/` | Postgres enforces row ownership via `auth.uid()` |
| 7. Rate limits | SlowAPI + `config_file.json` | Per-endpoint throttling by IP |
| 8. Logging hygiene | `custom_logger.py` | Redacts JWTs and emails from logs |

Failing any early layer returns a generic error when possible (especially auth), so probes learn little.

---

## 2. Middleware stack (order matters)

Registered in `main.py` so **incoming** execution order is:

1. **CORS** – only origins in `ALLOWED_ORIGINS` (env). Startup **aborts** if `*` is present.
2. **Security headers** – `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, strict CSP (`default-src 'none'`), `Referrer-Policy`, `Permissions-Policy`, and HSTS when HTTPS.
3. **Body size limit** – reject if `Content-Length` > 1 MB (`413`).
4. **JWT auth** – for non-public paths, require `Authorization: Bearer <jwt>`, validate JWT shape, then `supabase.auth.get_user(token)` (5s timeout). Attach `request.state.user` on success; otherwise generic `401 Authentication required.`

### Public paths (middleware skip)

These skip **Bearer** checks in `JWTAuthMiddleware`:

- `/`
- `/auth/sign_up_email`
- `/auth/log_in_email_pw`
- `/auth/reset_password`
- `/auth/refresh_token`
- `/security/retrieve_public_e_key`
- `/docs`, `/openapi.json`, `/redoc` (only if `DOCS_ENABLED=true`)
- `/miscellaneous/easter_egg_found` (handler still verifies token + email match)

Everything else (chat, profile, AI, logout, etc.) **requires** a valid Bearer header **before** the handler runs.

**Convention for clients (Postman / Flutter):**  
Protected routes need **both**:

- Header: `Authorization: Bearer <access_token>`
- Body field: `"access_token": "<same jwt>"` (handlers re-verify and use it for PostgREST)

Putting the token only in the body is not enough for middleware-protected routes.

---

## 3. Canonical protected-handler sequence

Most user-data endpoints follow this order (example: `user_chat_save`, `user_chat_retrieve`, `user_preferences`, `user_retrieve_profile`, `user_chat_delete`, `user_chat_titles_retrieve`, `ai_model_call`, `user_delete_profile`):

```text
1. Validate formats (access_token JWT shape, user_id UUID, …)
2. Create Supabase client with public/anon key
3. supabase.postgrest.auth(access_token)   # scope DB to this JWT
4. user = await supabase.auth.get_user(access_token)
5. Reject if user is None
6. Reject if user.id != body.user_id        # identity binding
7. Optional: ensure row exists in public.users
8. Perform business logic (select/insert/update/delete)
9. Rely on RLS as last line of defense
```

### Why identity binding matters

A valid access token must not authorize acting on an arbitrary `user_id`. Example from testing:

- Valid `access_token` for user A  
- Body `user_id` for user B  

→ Handler returns **401** (`User ID does not match authenticated user` / similar).  
This is intentional: tokens prove *who you are*; body IDs must match that identity.

### Email-bound variants

Some flows bind on email instead of (or in addition to) `user_id`:

- `complete_profile`: `user.email == body.email`, insert with `id: user.id`
- `easter_egg_found`: `user.email == body.email`

### Extra step-up for destructive actions

`user_delete_profile` adds:

1. Format validation (token, UUID, email, password)
2. Profile existence check
3. `get_user` + `user.id == user_id`
4. **Re-login** with `sign_in_with_password(email, password)` before delete
5. Admin delete only via **service role** client (`DB_SERVICE_KEY`), never for normal CRUD

---

## 4. AI endpoint convention (`/ai/generate_ai_response`)

Expensive / abuse-prone third-party calls must not run until auth succeeds:

1. Middleware Bearer check  
2. Validate token + `user_id` formats  
3. `get_user(access_token)` and `user.id == user_id` → else **401**  
4. **Then** `sanitize_prompt(prompt)`  
5. **Then** call Gemini (with model allowlist + timeout)

No valid session ⇒ no AI API call. Sanitization strips control/format Unicode, collapses whitespace, enforces max length (default 4000), rejects empty input.

Unknown `ai_model` values fall back to the configured default (no arbitrary model strings).

---

## 5. Input validation conventions

Centralized in `src/utils/validators.py` (and `sanitize.py` for prompts):

| Check | Rule (summary) |
|-------|----------------|
| Email | One `@`, allowed local chars, exactly one `.` in domain, provider + TLD allowlists from config |
| Password | Min 8 chars; upper, lower, digit, special |
| Access token | Three base64url segments separated by `.` (JWT shape) |
| Refresh token | Alphanumeric, length ≥ 10 |
| User ID | RFC 4122 UUID |
| Chat messages | Each item must match `MessageItem` (text, is_user, time_stamp) |

Invalid formats → **400** (often with generic wording like “Invalid encrypted credentials” where decrypt was planned).

Auth/token endpoints often return generic messages (`Authentication failed.`, `Token refresh failed.`) and `Cache-Control: no-store` so tokens are not cached by intermediaries.

---

## 6. Supabase / database conventions

Documented also in `supabase/README.md` and `supabase/migrations/README.md`.

### Identity model

- App profile table: `public.users` with **`id = auth.uid()`** (same UUID as Supabase Auth).
- Child tables (`user_conversations`, `user_preferences`, `ai_metrics`) key off `user_id` / ownership through FKs.
- Do **not** use a separate `auth_user_id` design (archived alternative only).

### Row Level Security (RLS)

RLS is enabled so that even a stolen anon key + forged query cannot freely read all rows:

- `public.users`: SELECT/INSERT/UPDATE/DELETE only where `id = auth.uid()`
- `public.user_conversations`: CRUD where `user_id = auth.uid()`
- `public.user_preferences`: CRUD where `user_id = auth.uid()`
- `public.ai_metrics`: SELECT/INSERT where `user_id = auth.uid()`
- `public.performance_engagement`: SELECT/INSERT only if linked `ai_metrics` row belongs to `auth.uid()`

Backend still checks identity in Python; RLS is the **database** safety net if the API is misused or PostgREST is hit directly.

### Grants

Roles `anon`, `authenticated`, `service_role` need `USAGE` on schema `public` and table privileges (see migration `00007_grant_schema.sql`). RLS policies alone are not enough without grants.

### Keys

| Key | Use |
|-----|-----|
| `DB_PUBLIC_KEY` (anon) | Normal client + JWT-scoped PostgREST |
| `DB_SERVICE_KEY` | Rare admin ops only (sign-up client, auth admin delete) |
| `CHAT_API_KEY` | Gemini only; never exposed to clients |
| `E_PUBLIC_KEY` | RSA public key for optional client-side encryption |

Never ship the service role key to the frontend. Prefer public key + user JWT for data access.

### Auth / storage / vault schemas

Reference dumps under `supabase/copied_schemas/` (or `schemas/`) are **not** application-owned. Auth is Supabase-managed; rebuild app logic via `migrations/`, not by replaying auth DDL.

---

## 7. Rate limiting

Every endpoint uses SlowAPI limits from `src/configuration/config_file.json` (requests per minute, etc.). Auth endpoints are intentionally low (e.g. 2–3/min) to slow credential stuffing; AI is higher but still capped.

---

## 8. Secrets, docs, and CORS

- Secrets and keys live in **environment variables**, not in source.
- OpenAPI `/docs` / `/redoc` / `/openapi.json` are **disabled** unless `DOCS_ENABLED=true`.
- CORS: explicit origin list; wildcard forbidden at startup.
- Optional RSA encrypt/decrypt for body fields exists (`en_de_crypt.py`) but is **commented out** in routers for now; the intended future pattern is: client encrypts with public key → server decrypts → then validate/auth.

---

## 9. Logging conventions

- Log auth outcomes and errors for ops.
- Do not log full JWTs or raw emails in clear form when the sensitive filter is active (`SensitiveDataFilter` redacts JWTs and emails).
- Prefer truncated token prefixes in debug (e.g. first 10 chars) if logging tokens at all.

---

## 10. Which endpoints need `Authorization: Bearer` — and why

### Why the header exists at all

`JWTAuthMiddleware` runs **before** every handler (except the public whitelist). It only reads the JWT from:

```http
Authorization: Bearer <access_token>
```

It does **not** read `access_token` from the JSON body. That is why Postman calls that only send the token in the body get `401 Authentication required.` on protected routes.

**Why require it on protected routes:** stop anonymous callers from even reaching handlers that touch user data, AI, or sessions. The body token is a **second** check used by the handler for PostgREST + identity binding.

**Why some routes skip the header:** they must work for users who are not logged in yet (sign-up, login, password reset, refresh, health, public encryption key). Those still validate their own inputs (email/password/refresh_token) inside the handler.

### Full endpoint table

| Method | Path | Bearer header required? | Body token / credentials | Why |
|--------|------|-------------------------|--------------------------|-----|
| `GET` | `/` | **No** | — | Health check; must be callable without a session. |
| `POST` | `/auth/sign_up_email` | **No** | `email`, `password` | User has no JWT yet; creates the account. |
| `POST` | `/auth/log_in_email_pw` | **No** | `email`, `password` | Issues the JWT; requiring Bearer would be circular. |
| `POST` | `/auth/reset_password` | **No** | `email` | User may be locked out / have no valid access token. |
| `POST` | `/auth/refresh_token` | **No** | `refresh_token` | Access token is expired; refresh token is the credential. |
| `POST` | `/security/retrieve_public_e_key` | **No** | — | Public RSA key for optional client encryption; safe to expose. |
| `POST` | `/auth/log_out` | **Yes** | `access_token` | Only the session owner should revoke their session; middleware proves JWT, body token is used to sign out. |
| `POST` | `/user_profile/complete_profile` | **Yes** | `access_token` + profile fields + `email` | Creates a profile row tied to the authenticated user; email must match token. |
| `POST` | `/user_profile/user_exists` | **Yes** | `access_token`, `user_id` | Existence check must run as an authenticated client (RLS); middleware blocks anonymous probes. |
| `POST` | `/user_profile/user_preferences` | **Yes** | `access_token`, `user_id`, … | Read/write preferences for **that** user only; Bearer + `user.id == user_id`. |
| `POST` | `/user_profile/user_retrieve_profile` | **Yes** | `access_token`, `user_id` | Returns private profile data; same identity binding. |
| `POST` | `/user_profile/user_delete_profile` | **Yes** | `access_token`, `user_id`, `email`, `password` | Destructive; Bearer + ID match + password re-entry before admin delete. |
| `POST` | `/chat/user_chat_save` | **Yes** | `access_token`, `user_id`, chat payload | Writes conversation data; wrong `user_id` with valid token → 401. |
| `POST` | `/chat/user_chat_retrieve` | **Yes** | `access_token`, `user_id`, … | Reads private chat history; same binding. |
| `POST` | `/chat/user_chat_titles_retrieve` | **Yes** | `access_token`, `user_id` | Lists titles for that user only. |
| `POST` | `/chat/user_chat_delete` | **Yes** | `access_token`, `user_id`, … | Deletes that user’s chats only. |
| `POST` | `/ai/generate_ai_response` | **Yes** | `access_token`, `user_id`, `prompt`, … | Prevents unpaid/anonymous abuse of Gemini; auth **before** API call. |
| `POST` | `/miscellaneous/easter_egg_found` | **No** (middleware whitelist) | `access_token`, `email` | Whitelisted in middleware, but handler still requires valid token + email match before updating the user row. Prefer sending Bearer anyway for consistency. |

### Client rules of thumb

1. If the path is **not** in the middleware public list → send **`Authorization: Bearer <jwt>`** or you never reach the handler.
2. If the handler accepts `access_token` in the body → send the **same** JWT there too (PostgREST + `get_user` / logout).
3. If the body has `user_id` → it must equal the user in that JWT, or you get 401 (identity binding).
4. Login / refresh responses: store both `access_token` and `refresh_token`; use refresh when access expires (no Bearer needed on `/auth/refresh_token`).

---

## 11. Checklist for a new project (reuse this logic)

1. **Public vs protected routes** – whitelist only what must be anonymous; everything else requires Bearer JWT verified with the IdP.
2. **Never trust body `user_id` alone** – always bind to `get_user(token).id` (or equivalent).
3. **Scope DB clients to the user JWT** – do not use the service role for normal CRUD.
4. **Enable RLS** on every user-owned table with `auth.uid()` (or equivalent) policies; grant schema/table privileges to API roles.
5. **Validate formats early** – UUID, JWT shape, email/password policy, structured payloads.
6. **Sanitize untrusted text** before sending to LLMs or storing as free text.
7. **Gate expensive side effects** (AI, email, SMS) behind successful auth.
8. **Step-up auth** for delete/account destruction (password re-entry + admin key only for admin APIs).
9. **Rate-limit** auth and AI harder than read-only endpoints.
10. **Generic errors** on auth failure; **no-store** on token responses; redact secrets in logs.
11. **CORS allowlist**, no `*`; **disable API docs** in production by default.
12. **Body size limits** and security headers on all responses.

---

## 12. Related files

| Topic | Location |
|-------|----------|
| App entry + CORS/docs/middleware wire-up | `main.py` |
| JWT middleware | `src/middleware/jwt_auth.py` |
| Headers / body limit | `src/middleware/security_headers.py`, `body_size_limit.py` |
| Validators / prompt sanitize | `src/utils/validators.py`, `src/utils/sanitize.py` |
| Example identity-bound chat write | `src/routers/chat/user_chat_save.py` |
| Example AI gate | `src/routers/ai/ai_model_call.py` |
| Step-up delete | `src/routers/user_profile/user_delete_profile.py` |
| RLS + grants | `supabase/migrations/00003_*.sql` … `00007_*.sql` |
| Rebuild DB | `supabase/README.md`, `supabase/migrations/README.md` |
| Schema reference (non-executable) | `supabase/copied_schemas/README.md` |

---

*Author: Sebastian Russo — conventions as implemented in this repository (2025–2026).*
