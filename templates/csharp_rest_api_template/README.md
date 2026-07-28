# C# REST API Template

A production-ready **ASP.NET Core 8** REST API template with config-driven endpoints and rate limits, CoreSpecs JSON, secure utility helpers, OpenAPI, Docker, and reference CRUD layers.

## Features

- ASP.NET Core controllers, OpenAPI JSON, and development Swagger UI.
- Central `CoreSpecs` JSON for network binding, logging, email policy, static data, endpoint paths, tags, and limits.
- Per-endpoint fixed-window rate limiting by client IP.
- Uniform JSON errors for 400, 404, 429, and 500 responses.
- Create/Update/Response DTO separation, service/repository layers, and a thread-safe in-memory example store.
- Configured custom file/console logger, validators, secure file I/O, RSA key generation, Docker, and xUnit tests.
- Optional Redis cache layer for services (off by default; rate limiting stays in-memory).

## Quick start

```powershell
cd templates/csharp_rest_api_template
Copy-Item .env.example .env
dotnet restore RestApiTemplate.sln
dotnet run --project src/RestApiTemplate
```

Requirements: .NET SDK 8+ and the matching **x64 ASP.NET Core 8 runtime**. Docker Desktop is optional for containers.

Once running:

- API root: `http://localhost:8080/`
- Health: `http://localhost:8080/health`
- Swagger UI (Development): `http://localhost:8080/docs`
- OpenAPI JSON (Development): `http://localhost:8080/api-docs/v1.json`

The helper scripts offer the same workflows:

```powershell
./start.ps1 dev
./start.ps1 test
./start.ps1 release
./start.ps1 docker
```

```sh
./start.sh dev
./start.sh test
```

## Project structure

```text
src/RestApiTemplate/
├── Configuration/       # CoreSpecs bridge, rate-limit attribute, utility startup
├── Controllers/         # Root plus one folder per endpoint group
├── CoreSpecs/           # Typed JSON loaders/models
├── DTOs/ Entities/      # API contracts and persisted representation
├── Errors/ Middleware/  # Uniform JSON errors and rate limiting
├── Repositories/        # Persistence abstraction + in-memory reference store
├── Resources/Cache/     # Optional Redis cache (RedisClient, RedisCacheService)
├── Services/            # Business logic
├── Utils/               # Adapted helpers from cs_various_utils
└── Resources/CoreSpecs/ # config_file.json and general_data.json
tests/RestApiTemplate.Tests/
```

## CoreSpecs configuration

`src/RestApiTemplate/Resources/CoreSpecs/Configuration/config_file.json` is loaded once before the host is built. It controls:

| Section | Responsibility |
|---|---|
| `network` | Host, bound port, optional context-path value |
| `logging` | Custom logger level, directory, and filename prefix |
| `email_validation` | Allowed providers and TLDs for `Validators` |
| `endpoints` | Prefix, route, OpenAPI tag, request limit, and time unit |
| `defaults` | Location of static `general_data.json` |

Example endpoint specification:

```json
"example_endpoint_1": {
  "request_limit": 10,
  "unit_of_time_for_limit": "m",
  "endpoint_prefix": "/subsection",
  "endpoint_tag": "example-items",
  "endpoint_route": "/items"
}
```

The template uses the endpoint key in three places: `Program.cs` builds the conventional route from `endpoint_prefix` plus `endpoint_route`; Swagger tags are derived from `endpoint_tag`; and `RateLimit("example_endpoint_1")` resolves the configured limit. Units are `s`, `m`, `h`, and `d`.

`general_data.json` is static, non-environment-specific reference data. The example item list logs its configured supported languages through `DataLoader`.

## Example API

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root health response (includes Redis status when configured) |
| GET | `/health` | ASP.NET health-check response (includes Redis status) |
| GET | `/subsection/items` | List example items |
| POST | `/subsection/items` | Create an item; optional `contactEmail` query value |
| GET | `/subsection/items/{id}` | Get one item (optional Redis cache demo) |
| PATCH | `/subsection/items/{id}` | Partial update |
| DELETE | `/subsection/items/{id}` | Delete an item |
| GET | `/subsection/status` | Second endpoint-group example |

## Adding an endpoint group

1. Add a uniquely named entry under `endpoints` in `config_file.json`.
2. Add a controller in its own `Controllers/<Group>/` folder.
3. Add `RateLimit("your_endpoint_key")` to every handler.
4. Register config-derived conventional route mappings in `Program.cs` using the new prefix and route values.
5. Add Create/Update/Response DTOs and, when persistence is required, entity, repository, and service classes.
6. Add integration tests for success, validation, not-found, and configured rate-limit behavior.

## Layers and utilities

- `DTOs`: request and response contracts; do not expose storage models directly.
- `Entities`: full persisted shape including server-controlled IDs.
- `Services`: business rules, ID generation, mapping, not-found behavior, and optional cache (see `ExampleItemService.GetById`).
- `Repositories`: swap `InMemoryExampleItemRepository` for EF Core, `SecureFileIo`, or another store.

## Optional Redis cache (`Resources/Cache/`)

Redis is **optional**. The application starts and serves requests when Redis is disabled or unreachable. The repository (or your future database) remains the source of truth; Redis is only for temporary cached data. **Rate limiting stays in-memory** unless you separately replace `RateLimiter` with a distributed store.

| Class | Role |
|---|---|
| `RedisClient` | Reads env config, connects when `REDIS_ENABLED=true`, exposes `GetStatus()` |
| `RedisCacheService` | `CacheGet`, `CacheSet`, `CacheDelete` — inject in services, not controllers |

**Enable locally:**

```bash
REDIS_ENABLED=true
REDIS_HOST=localhost
```

**Enable with Docker Compose** (Redis service is included in `docker-compose.yml`):

```bash
REDIS_ENABLED=true
REDIS_HOST=redis
```

**Health check** (`GET /` or `GET /health`):

| Redis state | `"redis"` value |
|---|---|
| Disabled | `"disabled"` |
| Connected | `"connected"` |
| Enabled but unreachable | `"unavailable"` |

**Usage in a service** (see `ExampleItemService.GetById`):

```csharp
public sealed class YourService(RedisCacheService cacheService)
{
    public YourResponse GetById(string id)
    {
        var cached = cacheService.CacheGet<YourResponse>($"entity:{id}");
        if (cached is not null) return cached;
        var response = LoadFromStore(id);
        cacheService.CacheSet($"entity:{id}", response, expirationSeconds: 600);
        return response;
    }
}
```

Controllers should call services — never inject `RedisClient` directly.

The `Utils/` files are copied and namespace-adapted from the repository's `cs_various_utils/` folder. `UtilityStartup` configures `CustomLogger`, `Validators`, and `SecureFileIo` from CoreSpecs. Application code uses `CustomLogger`; ASP.NET Core framework diagnostics retain their built-in logger.

`SecureFileIo` is confined to `Resources/`. Its YAML helpers are optional and require the consuming project to add `YamlDotNet`.

Generate development RSA keys only when an API feature needs them:

```powershell
dotnet run --project src/RestApiTemplate -- --generate-rsa-keys
```

The generated PEM files are ignored. The supplied C# utilities do not include an encryption helper; add a reviewed RSA OAEP-SHA256 implementation only when an API contract requires encrypted fields.

## Errors, logging, and scaling

Errors use `{ status, error, detail }`. The in-memory rate limiter is correct for a single instance; for multi-instance rate limits, replace `RateLimiter` with a Redis-backed counter separately from the optional cache layer in `Resources/Cache/`. Replace the example repository with EF Core and add migrations under `Resources/Db/Migrations` when needed.

At startup, `CustomLogger.Setup` creates `logs/<log_file_name>_<timestamp>.log`, writes startup entries, and receives application messages. `ApplicationStopping` flushes and closes the writer. Configure it with the `logging` CoreSpecs section; never commit logs or secrets.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose publishes `${HOST_PORT:-8080}:8080` and mounts `./logs`. The image builds/tests/publishes with the .NET 8 SDK, runs as a non-root user, and checks `/health`. Optional Redis for caching is included in `docker-compose.yml`; PostgreSQL remains a commented extension point.

## Tests and release checks

```powershell
dotnet build RestApiTemplate.sln
dotnet test RestApiTemplate.sln
dotnet publish src/RestApiTemplate --configuration Release --output ./publish
```

The suite covers CoreSpecs loading, utility configuration and path protection, rate limiting, CRUD services, and HTTP 200/201/400/404/429/500 responses.

## Environment variables

`.env` is used by Docker Compose and local tooling. Available variables:

| Variable | Description |
|---|---|
| `ASPNETCORE_ENVIRONMENT` | ASP.NET Core environment (Development, Production) |
| `HOST_PORT` | Container port mapping (default: 8080) |
| `HOST` | Application host binding (default: 0.0.0.0) |
| `RELOAD` | Hot reload toggle (default: false) |
| `WORKERS` | Number of worker processes (default: 1) |
| `E_PRIVATE_KEY` | RSA private key for encryption (replace in production) |
| `E_PRIVATE_PASSWORD` | RSA private key password (replace in production) |
| `E_PUBLIC_KEY` | RSA public key for encryption (replace in production) |
| `POSTGRES_DB` | PostgreSQL database name (uncomment if using database) |
| `POSTGRES_USER` | PostgreSQL username (uncomment if using database) |
| `POSTGRES_PASSWORD` | PostgreSQL password (uncomment if using database) |
| `DATABASE_URL` | PostgreSQL connection string (uncomment if using database) |
| `REDIS_ENABLED` | Enable optional Redis cache (`true` / `false`, default `false`) |
| `REDIS_HOST` | Redis host (`localhost` locally, `redis` in Docker Compose) |
| `REDIS_PORT` | Redis port (default `6379`) |
| `REDIS_PASSWORD` | Redis password (optional) |
| `REDIS_DB` | Redis database index (default `0`) |
| `LOG_LEVEL` | Logging level (default: info) |
| `API_TITLE` | OpenAPI title (default: Csharp REST API Template) |
| `API_VERSION` | OpenAPI version (default: 1.0.0) |
| `API_DESCRIPTION` | OpenAPI description |

The actual bound application host/port remain controlled by `CoreSpecs.network`.

## License

Provided as-is for educational and development purposes.
